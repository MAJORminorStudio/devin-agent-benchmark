import json
import csv
import io
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHARTS = ROOT / "assets/charts"


class PublicationAssetTests(unittest.TestCase):
    def test_publication_summary_matches_canonical_condition_totals(self):
        publication = json.loads((ROOT / "results/publication-summary.json").read_text())
        canonical = json.loads((ROOT / "results/experiment-002-summary.json").read_text())
        forensic = json.loads((ROOT / "results/experiment-002-forensics.json").read_text())
        e002 = publication["experiments"]["experiment-002"]["condition_metrics"]
        self.assertEqual(len(publication["cases"]), 5)
        self.assertEqual(publication["experiments"]["experiment-001"]["validity"], "operational_provenance_only")
        for label, condition in (("Medium", "M"), ("Max", "X")):
            expected = canonical["condition_summary"][condition]
            actual = e002[label]
            self.assertEqual(actual["solved"], expected["solved"])
            self.assertEqual(actual["wall_time_seconds"], expected["wall_time_seconds"])
            self.assertEqual(actual["steps"]["total"], sum(expected["steps"]["values_in_frozen_order"]))
            self.assertEqual(actual["tool_calls"]["total"], forensic["condition_summary"][condition]["total_tool_calls"])
            self.assertEqual(actual["tokens"]["prompt"], expected["tokens"]["prompt_total"])
            self.assertEqual(actual["tokens"]["completion"], expected["tokens"]["completion_total"])
            self.assertEqual(actual["tokens"]["cached"], expected["tokens"]["cached_total"])

    def test_publication_csv_has_all_five_cases(self):
        content = (ROOT / "results/publication-paired-results.csv").read_text()
        rows = list(csv.DictReader(io.StringIO(content)))
        self.assertEqual(len(rows), 5)
        self.assertEqual(
            {row["case"] for row in rows},
            {"black-16", "fastapi-3", "scrapy-3", "tqdm-5", "tornado-13"},
        )

    def test_all_required_charts_are_pngs(self):
        names = {
            "paired-wall-time.png",
            "success-rate.png",
            "total-token-use.png",
            "tool-calls-by-case.png",
            "steps-by-case.png",
            "source-vs-workspace-churn.png",
            "tqdm-case-study.png",
            "v2-paired-wall-time.png",
            "v2-success-by-dataset.png",
            "v2-resource-use.png",
            "v2-tqdm-heldout.png",
        }
        self.assertEqual({path.name for path in CHARTS.glob("*.png")}, names)
        for name in names:
            content = (CHARTS / name).read_bytes()
            self.assertTrue(content.startswith(b"\x89PNG\r\n\x1a\n"), name)
            self.assertGreater(len(content), 1000, name)


if __name__ == "__main__":
    unittest.main()
