#!/usr/bin/env python3
"""Validate private Experiment 005 ground truth without invoking an agent."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CASE_IDS = [f"E005-H{i:02d}" for i in range(1, 6)]
FORBIDDEN_AGENT_TEXT = (
    "E005",
    "E004",
    "E003",
    "Devin",
    "SWE-2",
    "reference",
    "heldout",
    "evaluator",
    "ground-truth",
    "construction",
)


def run_suite(command: list[str], cwd: Path) -> dict[str, Any]:
    forbidden_commands = {"devin", "devin-run.sh", "swe-2-medium", "swe-2-max"}
    if any(Path(token).name.lower() in forbidden_commands for token in command):
        raise RuntimeError(f"agent invocation is forbidden by this validator: {command}")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(cwd / "src")
    completed = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, check=False)
    return {
        "command": command,
        "returncode": completed.returncode,
        "status": "pass" if completed.returncode == 0 else "fail",
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def tree_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file() and "__pycache__" not in item.parts):
        digest.update(str(path.relative_to(root)).encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_patch(private_root: Path, case_id: str) -> str:
    case_root = private_root / "cases" / case_id
    buggy = case_root / "buggy" / "src"
    fixed = case_root / "fixed" / "src"
    paths = sorted({path.relative_to(buggy) for path in buggy.rglob("*.py")} | {path.relative_to(fixed) for path in fixed.rglob("*.py")})
    output: list[str] = []
    for relative in paths:
        left = (buggy / relative).read_text(encoding="utf-8").splitlines(keepends=True)
        right = (fixed / relative).read_text(encoding="utf-8").splitlines(keepends=True)
        if left != right:
            output.extend(
                difflib.unified_diff(
                    left,
                    right,
                    fromfile=f"a/src/{relative}",
                    tofile=f"b/src/{relative}",
                )
            )
    return "".join(output)


def make_agent_workspace(private_root: Path, case_id: str) -> Path:
    case_root = private_root / "cases" / case_id
    destination = private_root / "agent-workspaces" / case_id
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(case_root / "buggy", destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copy2(case_root / "TASK.md", destination / "TASK.md")
    return destination


def leak_audit(workspace: Path) -> dict[str, Any]:
    findings: list[str] = []
    disallowed_names = {"fixed", "evaluation", "metadata.json", "reference-patches"}
    for path in workspace.rglob("*"):
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        if path.name in disallowed_names or any(part in {"fixed", "evaluation"} for part in path.parts):
            findings.append(f"disallowed path: {path.relative_to(workspace)}")
            continue
        if path.is_file():
            content = path.read_text(encoding="utf-8", errors="replace")
            for marker in FORBIDDEN_AGENT_TEXT:
                if marker.lower() in content.lower():
                    findings.append(f"forbidden text {marker!r} in {path.relative_to(workspace)}")
    return {"status": "pass" if not findings else "fail", "findings": findings, "workspace": str(workspace)}


def validate_case(private_root: Path, case_id: str) -> dict[str, Any]:
    case_root = private_root / "cases" / case_id
    metadata = json.loads((case_root / "metadata.json").read_text(encoding="utf-8"))
    evaluation_root = private_root / "evaluation" / case_id
    commands = {
        "public": [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        "heldout": [sys.executable, "-m", "unittest", "discover", "-s", str(evaluation_root), "-p", "test_behavior.py", "-v"],
        "regression": [sys.executable, "-m", "unittest", "discover", "-s", str(evaluation_root), "-p", "test_regression.py", "-v"],
    }
    case_results: dict[str, Any] = {}
    deterministic: dict[str, Any] = {}
    for tree in ("buggy", "fixed"):
        cwd = case_root / tree
        first: dict[str, Any] = {}
        second: dict[str, Any] = {}
        for label, command in commands.items():
            first[label] = run_suite(command, cwd)
            second[label] = run_suite(command, cwd)
        first_status = {label: value["status"] for label, value in first.items()}
        second_status = {label: value["status"] for label, value in second.items()}
        if first_status != metadata["expected"][tree]:
            raise RuntimeError(f"{case_id} {tree} expected {metadata['expected'][tree]}, got {first_status}")
        if first_status != second_status:
            raise RuntimeError(f"{case_id} {tree} was not deterministic: {first_status} vs {second_status}")
        case_results[tree] = first
        deterministic[tree] = {"first": first_status, "second": second_status, "stable": True}
    workspace = make_agent_workspace(private_root, case_id)
    audit = leak_audit(workspace)
    if audit["status"] != "pass":
        raise RuntimeError(f"{case_id} leak audit failed: {audit['findings']}")
    return {
        "case_id": case_id,
        "expected": metadata["expected"],
        "results": case_results,
        "deterministic": deterministic,
        "leak_audit": audit,
        "buggy_tree_sha256": tree_sha256(case_root / "buggy"),
        "fixed_tree_sha256": tree_sha256(case_root / "fixed"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-root", type=Path, required=True)
    args = parser.parse_args()
    private_root = args.private_root.expanduser().resolve()
    patch_root = private_root / "reference-patches"
    patch_root.mkdir(parents=True, exist_ok=True)
    patch_hashes: dict[str, str] = {}
    for case_id in CASE_IDS:
        patch_path = patch_root / f"{case_id}.patch"
        patch_path.write_text(source_patch(private_root, case_id), encoding="utf-8")
        patch_hashes[case_id] = file_sha256(patch_path)
    cases = [validate_case(private_root, case_id) for case_id in CASE_IDS]
    timestamp = datetime.now(timezone.utc).isoformat()
    ground_truth = {"validation_version": 1, "validated_at_utc": timestamp, "cases": cases}
    deterministic = {
        "validation_version": 1,
        "validated_at_utc": timestamp,
        "status": "pass",
        "cases": [
            {"case_id": item["case_id"], "trees": item["deterministic"], "leak_audit": item["leak_audit"]}
            for item in cases
        ],
    }
    (private_root / "results").mkdir(parents=True, exist_ok=True)
    (private_root / "results" / "ground-truth-validation.json").write_text(json.dumps(ground_truth, indent=2) + "\n", encoding="utf-8")
    (private_root / "results" / "deterministic-validation.json").write_text(json.dumps(deterministic, indent=2) + "\n", encoding="utf-8")
    output = {
        "status": "pass",
        "cases": CASE_IDS,
        "reference_patch_sha256": patch_hashes,
        "ground_truth": str(private_root / "results" / "ground-truth-validation.json"),
        "deterministic": str(private_root / "results" / "deterministic-validation.json"),
        "devin_invocations": 0,
    }
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
