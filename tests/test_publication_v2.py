import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PublicationV2Tests(unittest.TestCase):
    def test_summary_has_twenty_valid_e002_e003_runs(self):
        summary = json.loads((ROOT / "results/publication-summary-v2.json").read_text())
        self.assertEqual(summary["publication_version"], "2.0.0")
        self.assertEqual(summary["denominator"]["valid_capability_runs"], 20)
        self.assertFalse(summary["denominator"]["e001_included"])
        self.assertEqual(len(summary["runs"]), 20)
        self.assertEqual({row["provenance"] for row in summary["runs"]}, {"historical", "novel"})
        self.assertEqual(summary["condition_summary"]["combined"]["M"]["solved"], 10)
        self.assertEqual(summary["condition_summary"]["combined"]["X"]["solved"], 9)
        self.assertEqual(summary["paired_outcomes"], {"both succeeded": 9, "Medium only": 1, "Max only": 0, "both failed": 0})

    def test_csv_has_all_twenty_runs_and_provenance(self):
        with (ROOT / "results/publication-paired-results-v2.csv").open(newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 20)
        self.assertEqual({row["provenance"] for row in rows}, {"historical", "novel"})
        self.assertEqual(sum(row["condition"] == "M" for row in rows), 10)
        self.assertEqual(sum(row["condition"] == "X" for row in rows), 10)

    def test_e003_public_case_bundle_has_both_trees_and_tests(self):
        for index in range(1, 6):
            case = ROOT / "artifacts/experiment-003/cases" / f"E003-N{index:02d}"
            for relative in ("buggy", "fixed", "buggy/tests", "evaluator/test_behavior.py", "evaluator/test_regression.py", "reference.patch", "case-manifest.json"):
                self.assertTrue((case / relative).exists(), relative)

    def test_report_and_charts_exist(self):
        self.assertTrue((ROOT / "reports/devin-swe2-reasoning-effort-v2.md").exists())
        for name in ("v2-paired-wall-time.png", "v2-success-by-dataset.png", "v2-resource-use.png", "v2-tqdm-heldout.png"):
            content = (ROOT / "assets/charts" / name).read_bytes()
            self.assertTrue(content.startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertGreater(len(content), 1000)


if __name__ == "__main__":
    unittest.main()
