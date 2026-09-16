import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import bugsinpy_harness as harness  # noqa: E402


class HarnessUnitTests(unittest.TestCase):
    def test_parse_info_handles_utf16_and_spacing(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bug.info"
            path.write_text(
                'python_version="3.8.3"\nfixed_commit_id = "abc"\n', encoding="utf-16"
            )
            self.assertEqual(harness.parse_info(path)["fixed_commit_id"], "abc")

    def test_parse_test_files_rejects_traversal(self):
        with self.assertRaises(SystemExit):
            harness.parse_test_files("tests/test_ok.py;../secret.py")

    def test_classify(self):
        self.assertEqual(harness.classify(0), "pass")
        self.assertEqual(harness.classify(1), "fail")
        self.assertEqual(harness.classify(124, timed_out=True), "error")

    def test_agent_audit_rejects_history_and_fixed_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            agent = Path(temp)
            (agent / ".git").mkdir()
            (agent / "leak.txt").write_text(
                "42a3fe53319a8c02858c2a96989ed1339f84515a", encoding="utf-8"
            )
            problems = harness.audit_agent_workspace(
                agent, "42a3fe53319a8c02858c2a96989ed1339f84515a"
            )
            self.assertTrue(any(".git" in item for item in problems))
            self.assertTrue(any("fixed commit hash" in item for item in problems))

    def test_manifest_has_ground_truth_fields(self):
        manifest = harness.load_manifest(ROOT / "manifests" / "experiment-001.json")
        self.assertEqual(len(manifest["cases"]), 5)
        self.assertTrue(
            all(case["fixed_commit"] and case["task_prompt"] for case in manifest["cases"])
        )

    def test_agent_prompts_match_manifest_without_ground_truth(self):
        manifest = harness.load_manifest(ROOT / "manifests" / "experiment-001.json")
        for case in manifest["cases"]:
            prompt = (ROOT / "prompts" / "experiment-001" / f"{case['case_id']}.md").read_text()
            self.assertIn(" ".join(case["task_prompt"].split()), " ".join(prompt.split()))
            self.assertNotIn(case["fixed_commit"], prompt)


if __name__ == "__main__":
    unittest.main()
