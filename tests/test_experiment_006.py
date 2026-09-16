import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE_IDS = [f"E006-K{i:02d}" for i in range(1, 6)] + [f"E006-H{i:02d}" for i in range(1, 6)]


class Experiment006FreezeTests(unittest.TestCase):
    def test_frozen_configuration_is_balanced_very_hard_tier(self):
        config = json.loads((ROOT / "manifests/experiment-006-config.json").read_text())
        self.assertEqual(config["experiment_id"], "experiment-006")
        self.assertEqual(config["status"], "frozen-ready-for-launch")
        self.assertEqual(config["tier"], "VERY-HARD capability-frontier")
        self.assertEqual([case["experiment_case_id"] for case in config["cases"]], CASE_IDS)
        self.assertEqual(sum(case["provenance"] == "historical-public" for case in config["cases"]), 5)
        self.assertEqual(sum(case["provenance"] == "newly-constructed-withheld" for case in config["cases"]), 5)
        self.assertEqual(config["tier_definition"]["unique_cases"], 10)
        self.assertEqual(config["tier_definition"]["runs"], 20)
        self.assertEqual(config["conditions"]["M"]["model"], "swe-2-medium")
        self.assertEqual(config["conditions"]["X"]["model"], "swe-2-max")
        self.assertEqual(config["limits"]["maximum_wall_time_seconds"], 7200)
        self.assertEqual(config["limits"]["retries"], 0)
        self.assertIsNone(config["limits"]["agent_step_limit"])
        self.assertIsNone(config["limits"]["agent_token_limit"])

    def test_run_order_is_exactly_balanced_and_not_blocked(self):
        manifest = json.loads((ROOT / "manifests/experiment-006-runs.json").read_text())
        runs = manifest["runs"]
        self.assertEqual(manifest["randomization"]["seed"], 20260926)
        self.assertEqual(len(runs), 20)
        self.assertEqual([run["run_index"] for run in runs], list(range(1, 21)))
        self.assertEqual(sorted(run["case_id"] for run in runs), sorted(CASE_IDS * 2))
        self.assertEqual(sum(run["condition"] == "M" for run in runs), 10)
        self.assertEqual(sum(run["condition"] == "X" for run in runs), 10)
        self.assertNotEqual([run["condition"] for run in runs], ["M"] * 10 + ["X"] * 10)
        for case_id in CASE_IDS:
            self.assertEqual({run["condition"] for run in runs if run["case_id"] == case_id}, {"M", "X"})

    def test_public_freeze_manifest_is_hash_only_for_private_material(self):
        freeze = json.loads((ROOT / "manifests/experiment-006-freeze.json").read_text())
        self.assertEqual(freeze["freeze_status"], "frozen-ready-for-launch")
        self.assertEqual(freeze["devin_invocations_before_freeze"], 0)
        self.assertEqual(freeze["swe2_invocations_before_freeze"], 0)
        self.assertEqual(set(freeze["case_hashes"]), set(CASE_IDS))
        for values in freeze["case_hashes"].values():
            for key, value in values.items():
                self.assertTrue(key.endswith("sha256"))
                self.assertRegex(value, r"^[0-9a-f]{64}$")
        serialized = json.dumps(freeze).lower()
        self.assertNotIn("test_behavior.py", serialized)
        self.assertNotIn("reference-patch", serialized)
        self.assertNotIn("private-run", serialized)

    def test_source_lock_and_security_contract_are_pinned(self):
        config = json.loads((ROOT / "manifests/experiment-006-config.json").read_text())
        self.assertEqual(config["source_lock"]["dataset_commit"], "316b95e2353ecda832bad9b42f86fa7c2fcec8ac")
        isolation = config["isolation_contract"]
        self.assertTrue(isolation["no_new_privileges"])
        self.assertEqual(isolation["capabilities"], "all dropped")
        self.assertFalse(isolation["direct_internet"])
        self.assertFalse(isolation["control_repository_mount"])
        self.assertFalse(isolation["docker_socket_mount"])


if __name__ == "__main__":
    unittest.main()
