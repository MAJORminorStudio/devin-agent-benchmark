import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / "scripts"))
import devin_runner  # noqa: E402
import export_case  # noqa: E402


class Phase2UnitTests(unittest.TestCase):
    def test_plan_is_noninteractive_swe2_and_fusion_free(self):
        config = devin_runner.read_json(ROOT / "manifests" / "experiment-001-config.json")
        case = {"case_id": "smoke", "experiment_case_id": "SMOKE-001"}
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp) / "workspace"
            workspace.mkdir()
            plan = devin_runner.plan_run(config, case, workspace, Path(temp) / "out", "devin", "swe-2-medium")
        self.assertFalse(plan["devin_invoked"])
        self.assertTrue(plan["noninteractive"])
        self.assertFalse(plan["fusion"]["enabled"])
        self.assertIn("--print", plan["command"])
        self.assertIn("--prompt-file", plan["command"])
        self.assertIn("--export", plan["command"])
        self.assertIn("swe-2-medium", plan["command"])

    def test_model_validation_rejects_fusion_and_unfrozen_models(self):
        config = devin_runner.read_json(ROOT / "manifests" / "experiment-001-config.json")
        with self.assertRaises(SystemExit):
            devin_runner.validate_model(config, "fusion-high")
        with self.assertRaises(SystemExit):
            devin_runner.validate_model(config, "swe-2-high")

    def test_export_audit_rejects_fixed_hash(self):
        fixed_hash = "f" * 40
        case = {
            "case_id": "synthetic",
            "project": "toy",
            "bug_id": "1",
            "buggy_commit": "b" * 40,
            "fixed_commit": fixed_hash,
            "test_files": [],
        }
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source"
            (source / "projects/toy/bugs/1").mkdir(parents=True)
            (source / "projects/toy/bugs/1/bug_patch.txt").write_text(
                "+++ b/toy.py\n+return the corrected value with sufficient length\n", encoding="utf-8"
            )
            (source / ".git").mkdir()
            destination = root / "export"
            destination.mkdir()
            (destination / "leak.txt").write_text(fixed_hash, encoding="utf-8")
            with self.assertRaises(SystemExit):
                export_case.audit_export(destination, case, source, audit_path=root / "audit.json")
            audit = json.loads((root / "audit.json").read_text(encoding="utf-8"))
            self.assertEqual(audit["status"], "fail")
            self.assertTrue(any("fixed commit" in item or fixed_hash in item for item in audit["problems"]))

    def test_workspace_case_rejects_ground_truth_fields(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp) / "workspace"
            workspace.mkdir()
            (workspace / "TASK.md").write_text("task\n", encoding="utf-8")
            (workspace / "SETUP.md").write_text("setup\n", encoding="utf-8")
            (workspace / "CASE.json").write_text(json.dumps({"case_id": "x", "fixed_commit": "secret"}), encoding="utf-8")
            (workspace.parent / "workspace.leak-audit.json").write_text(
                json.dumps({"status": "pass", "destination": str(workspace.resolve())}), encoding="utf-8"
            )
            with self.assertRaises(SystemExit):
                devin_runner.check_workspace(workspace)

    def test_frozen_run_manifest_has_balanced_interleaved_pairs(self):
        manifest = json.loads((ROOT / "manifests" / "experiment-001-runs.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["runs"]), 10)
        self.assertEqual(manifest["run_order"], [run["run_id"] for run in manifest["runs"]])
        self.assertEqual([run["condition"] for run in manifest["runs"]], ["M", "X", "M", "X", "M", "X", "M", "X", "M", "X"])
        for case_id in {run["case_id"] for run in manifest["runs"]}:
            self.assertEqual({run["condition"] for run in manifest["runs"] if run["case_id"] == case_id}, {"M", "X"})


if __name__ == "__main__":
    unittest.main()
