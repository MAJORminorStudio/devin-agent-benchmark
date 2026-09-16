#!/usr/bin/env python3
"""Validate private Experiment 005 ground truth without invoking an agent."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import os
import json
import shutil
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


HISTORICAL_CASE_IDS = [f"E005-K{i:02d}" for i in range(1, 6)]
NOVEL_CASE_IDS = [f"E005-H{i:02d}" for i in range(1, 6)]
CASE_IDS = HISTORICAL_CASE_IDS + NOVEL_CASE_IDS
FORBIDDEN_AGENT_TEXT = (
    "E005", "E004", "E003", "Devin", "SWE-2", "reference", "heldout",
    "evaluator", "ground-truth", "construction",
)


def run_suite(
    command: Sequence[str],
    cwd: Path,
    *,
    python_executable: Path,
    pythonpath: Sequence[Path],
) -> dict[str, Any]:
    forbidden_commands = {"devin", "devin-run.sh", "swe-2-medium", "swe-2-max"}
    if any(Path(token).name.lower() in forbidden_commands for token in command):
        raise RuntimeError(f"agent invocation is forbidden by this validator: {command}")
    actual = list(command)
    if actual and Path(actual[0]).name in {"python", "python3", "python3.8"}:
        actual[0] = str(python_executable)
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(str(path) for path in pythonpath)
    completed = subprocess.run(actual, cwd=cwd, env=env, text=True, capture_output=True, check=False)
    return {
        "command": actual,
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


def run_group(
    commands: Sequence[Sequence[str]],
    cwd: Path,
    *,
    python_executable: Path,
    pythonpath: Sequence[Path],
) -> dict[str, Any]:
    records = [run_suite(command, cwd, python_executable=python_executable, pythonpath=pythonpath) for command in commands]
    return {"status": "pass" if all(item["status"] == "pass" for item in records) else "fail", "commands": records}


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
            output.extend(difflib.unified_diff(left, right, fromfile=f"a/src/{relative}", tofile=f"b/src/{relative}"))
    return "".join(output)


def make_agent_workspace(private_root: Path, case_id: str, destination: Path | None = None) -> Path:
    case_root = private_root / "cases" / case_id
    destination = destination or private_root / "agent-workspaces" / case_id
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(case_root / "buggy", destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
    shutil.copy2(case_root / "TASK.md", destination / "TASK.md")
    return destination


def leak_audit(workspace: Path, *, fixed_commit: str | None = None, historical: bool = False) -> dict[str, Any]:
    findings: list[str] = []
    disallowed_names = {"fixed", "evaluation", "metadata.json", "reference-patches", "bug.info", "bug_patch.txt"}
    for path in workspace.rglob("*"):
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        if path.name in disallowed_names or any(part in {"fixed", "evaluation", "verification"} for part in path.parts):
            findings.append(f"disallowed path: {path.relative_to(workspace)}")
            continue
        if path.is_file():
            content = path.read_text(encoding="utf-8", errors="replace")
            if historical:
                if fixed_commit and fixed_commit in content:
                    findings.append(f"fixed revision present in {path.relative_to(workspace)}")
            else:
                for marker in FORBIDDEN_AGENT_TEXT:
                    if marker.lower() in content.lower():
                        findings.append(f"forbidden text {marker!r} in {path.relative_to(workspace)}")
    return {"status": "pass" if not findings else "fail", "findings": findings, "workspace": str(workspace)}


def historical_manifest(private_root: Path) -> dict[str, Any]:
    return json.loads((private_root / "historical-manifest.json").read_text(encoding="utf-8"))


def validate_case(private_root: Path, case_id: str, historical: Mapping[str, Any], historical_python: Path) -> dict[str, Any]:
    case_root = private_root / "cases" / case_id
    metadata = json.loads((case_root / "metadata.json").read_text(encoding="utf-8"))
    if case_id in HISTORICAL_CASE_IDS:
        source_case = next(item for item in historical["cases"] if item["case_id"] == case_id)
        public_commands = [shlex.split(command) for command in source_case["test_command"]]
        evaluator_python = historical_python
        evaluation_root = private_root / "evaluation" / case_id
        commands = {
            "public": public_commands,
            "heldout": [["python3", "-m", "unittest", "discover", "-s", str(evaluation_root), "-p", "test_behavior.py", "-q"]],
            "regression": [["python3", "-m", "unittest", "discover", "-s", str(evaluation_root), "-p", "test_regression.py", "-q"]],
        }
    else:
        evaluator_python = Path(sys.executable)
        commands = {
            "public": [[sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]],
            "heldout": [[sys.executable, "-m", "unittest", "discover", "-s", str(private_root / "evaluation" / case_id), "-p", "test_behavior.py", "-v"]],
            "regression": [[sys.executable, "-m", "unittest", "discover", "-s", str(private_root / "evaluation" / case_id), "-p", "test_regression.py", "-v"]],
        }
    case_results: dict[str, Any] = {}
    deterministic: dict[str, Any] = {}
    for tree in ("buggy", "fixed"):
        cwd = case_root / tree
        first: dict[str, Any] = {}
        second: dict[str, Any] = {}
        for label, command in commands.items():
            if case_id in HISTORICAL_CASE_IDS:
                paths = [cwd]
                if source_case.get("pythonpath"):
                    paths.insert(0, cwd / source_case["pythonpath"])
            else:
                paths = [cwd / "src"]
            first[label] = run_group(command, cwd, python_executable=evaluator_python, pythonpath=paths)
            second[label] = run_group(command, cwd, python_executable=evaluator_python, pythonpath=paths)
        first_status = {label: value["status"] for label, value in first.items()}
        second_status = {label: value["status"] for label, value in second.items()}
        if first_status != metadata["expected"][tree]:
            raise RuntimeError(f"{case_id} {tree} expected {metadata['expected'][tree]}, got {first_status}")
        if first_status != second_status:
            raise RuntimeError(f"{case_id} {tree} was not deterministic: {first_status} vs {second_status}")
        case_results[tree] = first
        deterministic[tree] = {"first": first_status, "second": second_status, "stable": True}
    workspace = make_agent_workspace(private_root, case_id)
    audit = leak_audit(workspace, fixed_commit=metadata.get("fixed_commit"), historical=case_id in HISTORICAL_CASE_IDS)
    if audit["status"] != "pass":
        raise RuntimeError(f"{case_id} leak audit failed: {audit['findings']}")
    run_audits = []
    for condition in ("M", "X"):
        run_id = f"{case_id}-{condition}"
        run_workspace = make_agent_workspace(private_root, case_id, private_root / "run-workspaces" / run_id)
        run_audit = leak_audit(run_workspace, fixed_commit=metadata.get("fixed_commit"), historical=case_id in HISTORICAL_CASE_IDS)
        if run_audit["status"] != "pass":
            raise RuntimeError(f"{run_id} leak audit failed: {run_audit['findings']}")
        run_audits.append({"run_id": run_id, "prompt_sha256": file_sha256(case_root / "TASK.md"), "audit": run_audit})
    prompt_hashes = {item["prompt_sha256"] for item in run_audits}
    if len(prompt_hashes) != 1:
        raise RuntimeError(f"{case_id} M/X prompts are not identical")
    return {
        "case_id": case_id,
        "expected": metadata["expected"],
        "results": case_results,
        "deterministic": deterministic,
        "leak_audit": audit,
        "run_leak_audits": run_audits,
        "prompt_pair_identity": {
            "M": run_audits[0]["prompt_sha256"],
            "X": run_audits[1]["prompt_sha256"],
            "identical": True,
        },
        "buggy_tree_sha256": tree_sha256(case_root / "buggy"),
        "fixed_tree_sha256": tree_sha256(case_root / "fixed"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-root", type=Path, required=True)
    parser.add_argument("--historical-python", type=Path, default=Path(sys.executable))
    args = parser.parse_args()
    private_root = args.private_root.expanduser().resolve()
    historical = historical_manifest(private_root)
    patch_root = private_root / "reference-patches"
    patch_root.mkdir(parents=True, exist_ok=True)
    patch_hashes: dict[str, str] = {}
    for case_id in CASE_IDS:
        patch_path = patch_root / f"{case_id}.patch"
        if case_id in NOVEL_CASE_IDS:
            patch_path.write_text(source_patch(private_root, case_id), encoding="utf-8")
        elif not patch_path.exists():
            source_case = next(item for item in historical["cases"] if item["case_id"] == case_id)
            dataset_patch = Path("/tmp/e005-bugsinpy.WJAGoI") / "projects" / source_case["project"] / "bugs" / str(source_case["bug_id"]) / "bug_patch.txt"
            shutil.copy2(dataset_patch, patch_path)
        patch_hashes[case_id] = file_sha256(patch_path)
    cases = [validate_case(private_root, case_id, historical, args.historical_python.expanduser().absolute()) for case_id in CASE_IDS]
    timestamp = datetime.now(timezone.utc).isoformat()
    ground_truth = {"validation_version": 2, "validated_at_utc": timestamp, "cases": cases}
    deterministic = {
        "validation_version": 2,
        "validated_at_utc": timestamp,
        "status": "pass",
        "cases": [{"case_id": item["case_id"], "trees": item["deterministic"], "leak_audit": item["leak_audit"]} for item in cases],
    }
    (private_root / "results").mkdir(parents=True, exist_ok=True)
    (private_root / "results" / "ground-truth-validation.json").write_text(json.dumps(ground_truth, indent=2) + "\n", encoding="utf-8")
    (private_root / "results" / "deterministic-validation.json").write_text(json.dumps(deterministic, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "pass",
        "cases": CASE_IDS,
        "reference_patch_sha256": patch_hashes,
        "ground_truth": str(private_root / "results" / "ground-truth-validation.json"),
        "deterministic": str(private_root / "results" / "deterministic-validation.json"),
        "devin_invocations": 0,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
