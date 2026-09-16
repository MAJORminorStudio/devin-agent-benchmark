import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE_IDS = [f"E004-N{i:02d}" for i in range(1, 6)]
RUN_IDS = {f"E004-N{i:02d}-{condition}" for i in range(1, 6) for condition in ("M", "X")}


class Experiment004ConfigurationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = json.loads((ROOT / "manifests/experiment-004-config.json").read_text())
        self.runs = json.loads((ROOT / "manifests/experiment-004-runs.json").read_text())

    def test_frozen_configuration_has_exactly_five_cases(self) -> None:
        self.assertEqual(self.config["experiment_id"], "experiment-004")
        self.assertEqual(self.config["status"], "frozen-ready-for-launch")
        self.assertEqual([case["case_id"] for case in self.config["cases"]], CASE_IDS)
        self.assertEqual(self.config["conditions"], {"M": "swe-2-medium", "X": "swe-2-max"})
        self.assertEqual(self.config["limits"]["maximum_wall_time_seconds"], 3600)
        self.assertIsNone(self.config["limits"]["agent_step_limit"])
        self.assertEqual(self.config["limits"]["retries"], 0)

    def test_run_order_is_balanced_interleaved_and_pair_separated(self) -> None:
        runs = self.runs["runs"]
        self.assertEqual(len(runs), 10)
        self.assertEqual([run["run_index"] for run in runs], list(range(1, 11)))
        self.assertEqual({run["run_id"] for run in runs}, RUN_IDS)
        self.assertEqual(sum(run["condition"] == "M" for run in runs), 5)
        self.assertEqual(sum(run["condition"] == "X" for run in runs), 5)
        conditions = [run["condition"] for run in runs]
        self.assertNotEqual(conditions, ["M"] * 5 + ["X"] * 5)
        self.assertNotEqual(conditions, ["X"] * 5 + ["M"] * 5)
        self.assertLessEqual(max(len(list(group)) for _, group in __import__("itertools").groupby(conditions)), 2)
        positions = {case_id: [] for case_id in CASE_IDS}
        for index, run in enumerate(runs):
            positions[run["case_id"]].append(index)
        self.assertTrue(all(values[1] - values[0] > 1 for values in positions.values()))

    def test_public_freeze_manifest_is_hash_only_for_case_content(self) -> None:
        freeze = json.loads((ROOT / "manifests/experiment-004-freeze.json").read_text())
        self.assertEqual(freeze["freeze_status"], "frozen-ready-for-launch")
        self.assertEqual(freeze["devin_invocations_before_freeze"], 0)
        self.assertEqual(freeze["swe2_invocations_before_freeze"], 0)
        self.assertEqual(set(freeze["case_hashes"]), set(CASE_IDS))
        for values in freeze["case_hashes"].values():
            for key, value in values.items():
                self.assertTrue(key.endswith("sha256"))
                self.assertRegex(value, re.compile(r"^[0-9a-f]{64}$"))


if __name__ == "__main__":
    unittest.main()
