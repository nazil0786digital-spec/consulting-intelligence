import unittest

from fastapi.testclient import TestClient

from app.main import app


class InvestigationPreviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_preview_returns_a_cited_four_part_evidence_pack(self) -> None:
        response = self.client.post(
            "/v1/investigations/preview",
            json={
                "organization_id": "demo-consulting",
                "issue_text": "PADER report counts differ after an upgrade to version 26.2.",
            },
        )

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(
            [item["category"] for item in result["evidence"]],
            ["verified_fact", "similar_case", "missing_information", "recommendation"],
        )
        self.assertTrue(result["evidence"][0]["citations"])

    def test_unknown_organization_cannot_access_fixture_corpus(self) -> None:
        response = self.client.post(
            "/v1/investigations/preview",
            json={"organization_id": "unapproved-org", "issue_text": "A sufficiently detailed issue description."},
        )
        self.assertEqual(response.status_code, 404)

    def test_local_web_origin_is_allowed(self) -> None:
        response = self.client.options(
            "/v1/investigations/preview",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["access-control-allow-origin"], "http://localhost:3000")
