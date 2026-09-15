#!/usr/bin/env python3
"""Create and audit private Experiment 003 agent workspaces.

Novel case source, prompts, evaluator tests, and reference material must live
outside the control repository. This tool intentionally refuses to copy any
fixed or evaluator-side path into an agent workspace.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CASE_IDS = [f"E003-N{i:02d}" for i in range(1, 6)]
FORBIDDEN_NAMES = {
    ".git", "metadata.json", "test_behavior.py", "test_regression.py",
    "reference.patch", "reference-fix.patch", "fixed", "evaluator",
}
FORBIDDEN_TEXT = (
    "E003", "experiment-003", "devin", "swe-2", "benchmark",
    "heldout", "hidden", "reference patch", "expected fix", "known fixed",
)


def die(message: str) -> "NoReturn":
    raise SystemExit(f"error: {message}")


def within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def digest_tree(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        rel = path.relative_to(root).as_posix()
        if "__pycache__" in path.parts:
            continue
        if path.is_symlink():
            digest.update(b"L\0" + rel.encode() + b"\0" + os.readlink(path).encode())
        elif path.is_file():
            digest.update(b"F\0" + rel.encode() + b"\0" + path.read_bytes())
    return digest.hexdigest()


def load_private_case(private_root: Path, case_id: str) -> dict[str, Any]:
    if case_id not in CASE_IDS:
        die(f"unknown case ID: {case_id}")
    metadata = private_root / "cases" / case_id / "metadata.json"
    try:
        value = json.loads(metadata.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        die(f"cannot read private metadata: {exc}")
    if value.get("case_id") != case_id:
        die(f"private metadata case mismatch: {case_id}")
    return value


def audit_workspace(workspace: Path, private_root: Path, case_id: str) -> dict[str, Any]:
    problems: list[str] = []
    source = private_root / "cases" / case_id / "buggy"
    if not workspace.is_dir():
        problems.append("workspace is missing")
    if within(workspace, REPO_ROOT):
        problems.append("workspace is inside the control repository")
    if within(workspace, private_root / "cases" / case_id / "fixed"):
        problems.append("workspace is inside the fixed tree")
    if (workspace / ".git").exists():
        problems.append("workspace contains git history")
    if workspace.is_dir():
        for path in sorted(workspace.rglob("*"), key=lambda item: item.relative_to(workspace).as_posix()):
            rel = path.relative_to(workspace).as_posix()
            if path.is_symlink():
                if not within(path, workspace):
                    problems.append(f"escaping symlink: {rel}")
                continue
            if path.name in FORBIDDEN_NAMES:
                problems.append(f"forbidden artifact name: {rel}")
            if path.is_dir() or path.name == "__pycache__":
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            lowered = text.lower()
            for token in FORBIDDEN_TEXT:
                if token.lower() in lowered:
                    problems.append(f"forbidden text in {rel}: {token}")
            if str(private_root) in text or str(REPO_ROOT) in text:
                problems.append(f"private/control path in {rel}")
            if (source / rel).is_file() and path.read_bytes() != (source / rel).read_bytes():
                if rel != "TASK.md":
                    problems.append(f"workspace source differs from buggy baseline: {rel}")
    return {
        "audit_version": 1,
        "case_id": case_id,
        "workspace": str(workspace),
        "workspace_sha256": digest_tree(workspace) if workspace.is_dir() else None,
        "status": "pass" if not problems else "fail",
        "problems": problems,
    }


def export_workspace(private_root: Path, case_id: str, destination: Path, force: bool) -> dict[str, Any]:
    metadata = load_private_case(private_root, case_id)
    source = private_root / "cases" / case_id / "buggy"
    prompt = private_root / "prompts" / f"{case_id}.md"
    if not source.is_dir() or not prompt.is_file():
        die(f"private source or prompt missing for {case_id}")
    destination = destination.expanduser().resolve()
    if within(destination, REPO_ROOT):
        die("agent workspace must be outside the control repository")
    if destination.exists():
        if not force:
            die(f"destination exists; use --force only for a named disposable workspace: {destination}")
        shutil.rmtree(destination)
    shutil.copytree(source, destination, symlinks=True, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    (destination / "TASK.md").write_text(prompt.read_text(encoding="utf-8").rstrip() + "\n", encoding="utf-8")
    audit = audit_workspace(destination, private_root, case_id)
    audit_path = destination.parent / f"{destination.name}.leak-audit.json"
    audit_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if audit["status"] != "pass":
        die("workspace leak audit failed: " + "; ".join(audit["problems"]))
    return {"case_id": case_id, "metadata_project": metadata["project_name"], "audit": audit}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-root", type=Path, required=True)
    parser.add_argument("--case-id", choices=CASE_IDS, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    result = export_workspace(args.private_root.expanduser().resolve(), args.case_id, args.destination, args.force)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
