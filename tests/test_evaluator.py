import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import evaluate_run  # noqa: E402


class EvaluatorScoringTests(unittest.TestCase):
    def test_heldout_not_run_cannot_produce_success(self):
        score = evaluate_run.score_evaluation(
            {"overall": "pass"},
            {"overall": "not-run"},
            {"overall": "pass"},
        )
        self.assertEqual(score["evaluation_status"], "EVALUATION_ERROR")
        self.assertIsNone(score["task_success"])

    def test_evaluator_error_is_not_agent_failure(self):
        score = evaluate_run.score_evaluation(
            {"overall": "pass"},
            {"overall": "error"},
            {"overall": "pass"},
        )
        self.assertEqual(score["evaluation_status"], "EVALUATION_ERROR")
        self.assertIsNone(score["task_success"])

    def test_success_requires_public_heldout_and_regression_passes(self):
        score = evaluate_run.score_evaluation(
            {"overall": "pass"},
            {"overall": "pass"},
            {"overall": "pass"},
        )
        self.assertEqual(score["evaluation_status"], "OK")
        self.assertIs(score["task_success"], True)
        self.assertEqual(score["regression_status"], "clean")


if __name__ == "__main__":
    unittest.main()
