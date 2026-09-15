import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Experiment003ConfigurationTests(unittest.TestCase):
    def test_frozen_configuration_has_five_cases_and_two_conditions(self):
        config = json.loads((ROOT / "manifests/experiment-003-config.json").read_text())
        self.assertEqual(config["experiment_id"], "experiment-003")
        self.assertEqual(config["status"], "frozen-ready-for-launch")
        self.assertEqual([case["case_id"] for case in config["cases"]], [f"E003-N{i:02d}" for i in range(1, 6)])
        self.assertEqual(config["conditions"], {"M": "swe-2-medium", "X": "swe-2-max"})
        self.assertEqual(config["limits"]["maximum_wall_time_seconds"], 3600)
        self.assertEqual(config["limits"]["retries"], 0)

    def test_run_order_is_balanced_and_interleaved(self):
        runs = json.loads((ROOT / "manifests/experiment-003-runs.json").read_text())["runs"]
        self.assertEqual(len(runs), 10)
        self.assertEqual([run["run_index"] for run in runs], list(range(1, 11)))
        self.assertEqual(sorted(run["run_id"] for run in runs), sorted(f"E003-N{i:02d}-{c}" for i in range(1, 6) for c in ("M", "X")))
        self.assertEqual(sum(run["condition"] == "M" for run in runs), 5)
        self.assertEqual(sum(run["condition"] == "X" for run in runs), 5)
        self.assertNotEqual([run["condition"] for run in runs], ["M"] * 5 + ["X"] * 5)

    def test_public_freeze_manifest_contains_hashes_not_case_contents(self):
        freeze = json.loads((ROOT / "manifests/experiment-003-freeze.json").read_text())
        self.assertEqual(freeze["freeze_status"], "frozen-ready-for-launch")
        self.assertEqual(freeze["devin_invocations_before_freeze"], 0)
        self.assertEqual(set(freeze["case_hashes"]), {f"E003-N{i:02d}" for i in range(1, 6)})
        for values in freeze["case_hashes"].values():
            for key, value in values.items():
                self.assertTrue(key.endswith("sha256"))
                self.assertRegex(value, r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
