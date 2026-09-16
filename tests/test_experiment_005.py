import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Experiment005ConfigurationTests(unittest.TestCase):
    def test_frozen_configuration_has_balanced_hard_tier_and_two_conditions(self):
        config = json.loads((ROOT / "manifests/experiment-005-config.json").read_text())
        self.assertEqual(config["experiment_id"], "experiment-005")
        self.assertEqual(config["status"], "frozen-ready-for-launch")
        self.assertEqual([case["case_id"] for case in config["cases"]], [f"E005-K{i:02d}" for i in range(1, 6)] + [f"E005-H{i:02d}" for i in range(1, 6)])
        self.assertEqual(sum(case["provenance"] == "historical-public" for case in config["cases"]), 5)
        self.assertEqual(sum(case["provenance"] == "newly-constructed-withheld" for case in config["cases"]), 5)
        self.assertEqual(config["tier_definition"]["unique_cases"], 10)
        self.assertEqual(config["tier_definition"]["runs"], 20)
        self.assertEqual(config["conditions"], {"M": "swe-2-medium", "X": "swe-2-max"})
        self.assertEqual(config["limits"]["maximum_wall_time_seconds"], 5400)
        self.assertEqual(config["limits"]["retries"], 0)

    def test_run_order_is_balanced_pairwise_and_interleaved(self):
        manifest = json.loads((ROOT / "manifests/experiment-005-runs.json").read_text())
        runs = manifest["runs"]
        self.assertEqual(manifest["randomization"]["seed"], 20260918)
        self.assertEqual(len(runs), 20)
        self.assertEqual([run["run_index"] for run in runs], list(range(1, 21)))
        case_ids = [f"E005-K{i:02d}" for i in range(1, 6)] + [f"E005-H{i:02d}" for i in range(1, 6)]
        self.assertEqual(sorted(run["run_id"] for run in runs), sorted(f"{case_id}-{c}" for case_id in case_ids for c in ("M", "X")))
        self.assertEqual(sum(run["condition"] == "M" for run in runs), 10)
        self.assertEqual(sum(run["condition"] == "X" for run in runs), 10)
        self.assertNotEqual([run["condition"] for run in runs], ["M"] * 5 + ["X"] * 5)
        for case_id in case_ids:
            self.assertEqual({run["condition"] for run in runs if run["case_id"] == case_id}, {"M", "X"})
        self.assertEqual({run["provenance"] for run in runs}, {"historical-public", "newly-constructed-withheld"})

    def test_public_freeze_manifest_contains_hashes_only(self):
        freeze = json.loads((ROOT / "manifests/experiment-005-freeze.json").read_text())
        self.assertEqual(freeze["freeze_status"], "frozen-ready-for-launch")
        self.assertEqual(freeze["devin_invocations_before_freeze"], 0)
        self.assertEqual(freeze["swe2_invocations_before_freeze"], 0)
        self.assertEqual(set(freeze["case_hashes"]), {f"E005-{p}{i:02d}" for p in ("K", "H") for i in range(1, 6)})
        for values in freeze["case_hashes"].values():
            for key, value in values.items():
                self.assertTrue(key.endswith("sha256"))
                self.assertRegex(value, r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
