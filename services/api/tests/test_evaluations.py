import unittest

from fastapi.testclient import TestClient

from app.main import app


class EvaluationTests(unittest.TestCase):
    def test_baseline_suite_passes_and_uses_sanitized_scenarios(self) -> None:
        with TestClient(app) as client:
            response = client.get("/v1/evaluations/baseline")
        self.assertEqual(response.status_code, 200)
        report = response.json()
        self.assertEqual(report["suite"], "phase_3_baseline")
        self.assertEqual(report["passed_cases"], report["total_cases"])
        self.assertTrue(all(result["checks"]["expected_citations_returned"] for result in report["results"]))
