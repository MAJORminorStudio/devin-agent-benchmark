#!/usr/bin/env python3
"""Validate private Experiment 003 ground truth without invoking Devin."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CASE_IDS = [f"E003-N{i:02d}" for i in range(1, 6)]


def run(command: list[str], cwd: Path) -> dict[str, Any]:
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


def validate_case(private_root: Path, case_id: str) -> dict[str, Any]:
    case_root = private_root / "cases" / case_id
    metadata = json.loads((case_root / "metadata.json").read_text(encoding="utf-8"))
    evaluation_root = private_root / "evaluation" / case_id
    results: dict[str, Any] = {}
    for tree in ("buggy", "fixed"):
        cwd = case_root / tree
        public = run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd)
        heldout = run([sys.executable, "-m", "unittest", "discover", "-s", str(evaluation_root), "-p", "test_behavior.py", "-v"], cwd)
        regression = run([sys.executable, "-m", "unittest", "discover", "-s", str(evaluation_root), "-p", "test_regression.py", "-v"], cwd)
        expected = metadata["expected"][tree]
        actual = {key: value["status"] for key, value in {"public": public, "heldout": heldout, "regression": regression}.items()}
        if actual != expected:
            raise RuntimeError(f"{case_id} {tree} expected {expected}, got {actual}")
        results[tree] = {"public": public, "heldout": heldout, "regression": regression}
    return {"case_id": case_id, "expected": metadata["expected"], "results": results}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-root", type=Path, required=True)
    args = parser.parse_args()
    private_root = args.private_root.expanduser().resolve()
    all_results = {
        "validation_version": 1,
        "validated_at_utc": datetime.now(timezone.utc).isoformat(),
        "cases": [validate_case(private_root, case_id) for case_id in CASE_IDS],
    }
    output = private_root / "results" / "ground-truth-validation.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(all_results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "status": "pass", "cases": CASE_IDS}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
