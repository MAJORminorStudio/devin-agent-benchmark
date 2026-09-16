#!/usr/bin/env python3
"""Exercise export, leak-audit, dry-run, and evaluator plumbing on a toy case.

The smoke case is disposable and is not one of the five BugsInPy cases. It
never invokes Devin. The synthetic workspace is fixed only to validate patch
capture and evaluation mechanics.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bugsinpy_harness as harness  # noqa: E402
import devin_runner  # noqa: E402
import export_case  # noqa: E402
import evaluate_run  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run() -> dict:
    with tempfile.TemporaryDirectory(prefix="devin-benchmark-smoke-") as temp_name:
        root = Path(temp_name)
        source = root / "synthetic-bugsinpy"
        bug_dir = source / "projects" / "toycalc" / "bugs" / "1"
        bug_dir.mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(source)], check=True)
        fixed_hash = "2" * 40
        buggy_hash = "1" * 40
        write(
            bug_dir / "bug_patch.txt",
            """diff --git a/calculator.py b/calculator.py
--- a/calculator.py
+++ b/calculator.py
@@
-    return left - right
+    return left + right  # synthetic reference behavior for smoke only
""",
        )
        case = {
            "case_id": "synthetic-1",
            "experiment_case_id": "SMOKE-001",
            "source": "BugsInPy",
            "project": "toycalc",
            "bug_id": "1",
            "original_repository": "https://example.invalid/toycalc",
            "python_version": "3.11",
            "buggy_commit": buggy_hash,
            "fixed_commit": fixed_hash,
            "test_files": ["test_public.py"],
            "test_command": ["python -m unittest -q test_public.TestAddition.test_add"],
            "expected_buggy_result": "fail",
            "expected_fixed_result": "pass",
            "task_prompt": "The toy addition function returns the wrong result. Reproduce the failing public test, diagnose the cause, implement a focused fix, and run the test.",
            "difficulty": "smoke",
            "status": "synthetic",
        }
        manifest = root / "manifest.json"
        write(manifest, json.dumps({"experiment_id": "smoke", "cases": [case]}, indent=2) + "\n")
        run_root = root / "run" / "synthetic-1"
        agent_source = run_root / "agent-workspace"
        metadata = run_root / "metadata"
        agent_source.mkdir(parents=True)
        metadata.mkdir(parents=True)
        write(agent_source / "calculator.py", "def add(left, right):\n    return left - right\n")
        write(agent_source / "test_public.py", "import unittest\nfrom calculator import add\n\nclass TestAddition(unittest.TestCase):\n    def test_add(self):\n        self.assertEqual(add(2, 3), 5)\n")
        write(run_root / "prepare.json", json.dumps({"agent_workspace_audit": "pass"}) + "\n")
        write(run_root / "reproducibility.json", json.dumps({"case_id": "synthetic-1", "reproducible": True, "sides": {"buggy": {"overall": "fail"}, "fixed": {"overall": "pass"}}}) + "\n")

        exported = root / "exported"
        export_record = export_case.export_case(manifest, "synthetic-1", run_root, source, exported, False)
        workspace_case = export_case.read_json(exported / "CASE.json")
        plan_dir = root / "plan"
        config = devin_runner.read_json(REPO_ROOT / "manifests" / "experiment-001-config.json")
        plan = devin_runner.plan_run(config, workspace_case, exported, plan_dir, "devin", config["agent"]["model"])
        plan_dir.mkdir()
        (plan_dir / "dry-run-plan.json").write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")

        # This is a toy-only mutation used to prove the evaluator can capture
        # a patch. No BugsInPy source or Experiment 001 case is modified.
        write(exported / "calculator.py", "def add(left, right):\n    return left + right\n")
        hidden = root / "hidden-evaluator"
        write(hidden / "test_hidden.py", "import os\nimport sys\nsys.path.insert(0, os.environ['SMOKE_AGENT'])\nfrom calculator import add\nassert add(-2, 7) == 5\n")
        reference = root / "reference.patch"
        write(reference, "+++ b/calculator.py\n+    return left + right  # synthetic reference behavior for smoke only\n")
        eval_dir = root / "evaluation"
        old_agent = os.environ.get("SMOKE_AGENT")
        os.environ["SMOKE_AGENT"] = str(exported)
        try:
            result = evaluate_run.main([
                "--manifest", str(manifest),
                "--case-id", "synthetic-1",
                "--run-root", str(run_root),
                "--workspace", str(exported),
                "--output-dir", str(eval_dir),
                "--baseline-dir", str(root / "exported.baseline"),
                "--hidden-workspace", str(hidden),
                "--hidden-command", "python test_hidden.py",
                "--reference-patch", str(reference),
            ])
        finally:
            if old_agent is None:
                os.environ.pop("SMOKE_AGENT", None)
            else:
                os.environ["SMOKE_AGENT"] = old_agent
        if result != 0:
            raise SystemExit("smoke evaluation failed")
        audit = export_case.read_json(root / "exported.leak-audit.json")
        evaluation = evaluate_run.read_json(eval_dir / "evaluation-result.json")
        return {
            "smoke_case": "synthetic-1",
            "export_audit": audit["status"],
            "dry_run_devin_invoked": plan["devin_invoked"],
            "dry_run_command_uses_swe2": "swe-2-medium" in plan["command"],
            "hidden_tests_stayed_evaluator_side": not (exported / "test_hidden.py").exists(),
            "evaluation_pass": evaluation["pass"],
            "patch_captured": bool(evaluation["patch"]["sha256"]),
            "devin_invoked": False,
            "export_record": export_record,
        }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
