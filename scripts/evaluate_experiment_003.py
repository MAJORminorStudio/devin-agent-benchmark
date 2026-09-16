#!/usr/bin/env python3
"""Evaluate a closed E003 workspace using private evaluator-side tests."""

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

REPO_ROOT = Path(__file__).resolve().parents[1]
CASE_IDS = [f"E003-N{i:02d}" for i in range(1, 6)]


def die(message: str) -> "NoReturn":
    raise SystemExit(f"error: {message}")


def run(command: list[str], cwd: Path, *, test_root: Path | None = None) -> dict[str, Any]:
    env = os.environ.copy()
    paths = [str(cwd / "src")]
    if test_root is not None:
        paths.insert(0, str(test_root))
    env["PYTHONPATH"] = os.pathsep.join(paths)
    completed = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, check=False)
    return {
        "command": command,
        "returncode": completed.returncode,
        "status": "pass" if completed.returncode == 0 else "fail",
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def entries(root: Path) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        if path.is_file() and "__pycache__" not in path.parts:
            result[path.relative_to(root).as_posix()] = path.read_bytes()
    return result


def patch_for(baseline: Path, workspace: Path) -> tuple[str, list[str], dict[str, int]]:
    before, after = entries(baseline), entries(workspace)
    changed = sorted(set(before) | set(after))
    lines: list[str] = []
    files: list[str] = []
    additions = deletions = 0
    for rel in changed:
        if before.get(rel) == after.get(rel):
            continue
        files.append(rel)
        old = before.get(rel, b"").decode("utf-8", "replace").splitlines(keepends=True)
        new = after.get(rel, b"").decode("utf-8", "replace").splitlines(keepends=True)
        diff = list(difflib.unified_diff(old, new, fromfile=f"a/{rel}", tofile=f"b/{rel}"))
        lines.extend(diff)
        additions += sum(line.startswith("+") and not line.startswith("+++") for line in diff)
        deletions += sum(line.startswith("-") and not line.startswith("---") for line in diff)
    text = "".join(lines)
    return text, files, {"additions": additions, "deletions": deletions, "sha256": hashlib.sha256(text.encode()).hexdigest()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-root", type=Path, required=True)
    parser.add_argument("--case-id", choices=CASE_IDS, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    private = args.private_root.expanduser().resolve()
    workspace = args.workspace.expanduser().resolve()
    baseline = (args.baseline or workspace.parent / f"{workspace.name}.baseline").expanduser().resolve()
    output = args.output_dir.expanduser().resolve()
    if not workspace.is_dir() or not (workspace / "TASK.md").is_file():
        die("closed workspace must contain TASK.md")
    if not baseline.is_dir() or baseline == workspace:
        die("private buggy baseline is missing or invalid")
    if not output.is_dir() and output.exists():
        die("output path is not a directory")
    if output.exists() and any(output.iterdir()):
        die("output directory must be fresh")
    try:
        workspace.relative_to(REPO_ROOT)
        die("workspace must be outside control repository")
    except ValueError:
        pass
    metadata_path = private / "cases" / args.case_id / "metadata.json"
    evaluator_root = private / "evaluation" / args.case_id
    if not metadata_path.is_file() or not (evaluator_root / "test_behavior.py").is_file() or not (evaluator_root / "test_regression.py").is_file():
        die("EVALUATION_ERROR: private evaluator inputs are incomplete")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    output.mkdir(parents=True, exist_ok=True)
    public = run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], workspace)
    heldout = run([sys.executable, "-m", "unittest", "discover", "-s", str(evaluator_root), "-p", "test_behavior.py", "-v"], workspace, test_root=evaluator_root)
    regression = run([sys.executable, "-m", "unittest", "discover", "-s", str(evaluator_root), "-p", "test_regression.py", "-v"], workspace, test_root=evaluator_root)
    patch, changed_files, patch_metrics = patch_for(baseline, workspace)
    (output / "agent.patch").write_text(patch, encoding="utf-8")
    result = {
        "evaluation_version": 1,
        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
        "experiment_id": "experiment-003",
        "case_id": args.case_id,
        "workspace": str(workspace),
        "public": public,
        "heldout": heldout,
        "regression": regression,
        "task_success": all(item["status"] == "pass" for item in (public, heldout, regression)),
        "evaluation_status": "OK",
        "changed_files": changed_files,
        "patch": patch_metrics,
        "reference_patch_compared": False,
        "metadata_project": metadata["project_name"],
    }
    (output / "evaluation-result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"case_id": args.case_id, "task_success": result["task_success"], "evaluation_status": "OK", "output": str(output)}, indent=2))
    return 0 if result["task_success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
