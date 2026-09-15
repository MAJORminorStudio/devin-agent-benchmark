#!/usr/bin/env python3
"""Export one private buggy tree as an audited agent-visible workspace."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any, NoReturn


REPO_ROOT = Path(__file__).resolve().parents[1]
CASE_IDS = [f"E004-N{i:02d}" for i in range(1, 6)]
FORBIDDEN_NAMES = {".git", "metadata.json", "reference.patch", "fixed", "evaluator"}
FORBIDDEN_TEXT = (
    "e004", "experiment-004", "devin", "swe-2", "benchmark", "intentional bug",
    "hidden test", "held-out", "heldout", "reference fix", "expected patch",
    "experimental metadata", "solution",
)


def die(message: str) -> NoReturn:
    raise SystemExit(f"error: {message}")


def inside(candidate: Path, parent: Path) -> bool:
    try:
        candidate.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def digest_tree(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        if "__pycache__" in path.parts:
            continue
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            digest.update(b"L\0" + relative.encode() + b"\0" + os.readlink(path).encode())
        elif path.is_file():
            digest.update(b"F\0" + relative.encode() + b"\0" + path.read_bytes())
    return digest.hexdigest()


def audit(workspace: Path, source: Path) -> dict[str, Any]:
    problems: list[str] = []
    for path in sorted(workspace.rglob("*"), key=lambda item: item.relative_to(workspace).as_posix()):
        relative = path.relative_to(workspace).as_posix()
        if path.is_dir() or path.name == "__pycache__":
            continue
        if path.name in FORBIDDEN_NAMES:
            problems.append(f"forbidden artifact name: {relative}")
        contents = path.read_text(encoding="utf-8", errors="ignore").lower()
        for token in FORBIDDEN_TEXT:
            if token in contents:
                problems.append(f"forbidden text in {relative}: {token}")
        if relative != "TASK.md" and (source / relative).is_file() and path.read_bytes() != (source / relative).read_bytes():
            problems.append(f"source differs from private buggy tree: {relative}")
    if not (workspace / "TASK.md").is_file():
        problems.append("TASK.md is missing")
    return {
        "audit_version": 1, "workspace": str(workspace), "workspace_sha256": digest_tree(workspace),
        "status": "pass" if not problems else "fail", "problems": problems,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-root", type=Path, required=True)
    parser.add_argument("--case-id", choices=CASE_IDS, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    private_root = args.private_root.expanduser().resolve()
    source = private_root / "cases" / args.case_id / "buggy"
    prompt = private_root / "prompts" / f"{args.case_id}.md"
    destination = args.destination.expanduser().resolve()
    if not source.is_dir() or not prompt.is_file():
        die("private buggy tree or prompt is missing")
    if inside(destination, REPO_ROOT):
        die("agent workspace must be outside the control repository")
    if destination.exists():
        if not args.force:
            die("destination exists; use --force for a named disposable workspace")
        shutil.rmtree(destination)
    shutil.copytree(source, destination, symlinks=True, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    (destination / "TASK.md").write_text(prompt.read_text(encoding="utf-8").rstrip() + "\n", encoding="utf-8")
    result = audit(destination, source)
    (destination.parent / f"{destination.name}.leak-audit.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "pass":
        die("workspace leak audit failed: " + "; ".join(result["problems"]))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
