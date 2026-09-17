import unittest
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


class InvestigationPreviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.client.__enter__()

    def tearDown(self) -> None:
        self.client.__exit__(None, None, None)

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

    def test_organization_can_upload_and_read_its_text_document_status(self) -> None:
        organization = self.client.post("/v1/organizations", json={"name": f"Upload test {uuid4()}"})
        self.assertEqual(organization.status_code, 201)
        organization_id = organization.json()["id"]

        upload = self.client.post(
            f"/v1/organizations/{organization_id}/documents",
            data={"source_type": "release_note"},
            files={"file": ("release-notes.txt", b"Release note content for PADER report count validation after version 26.2 upgrade. " * 200, "text/plain")},
        )
        self.assertEqual(upload.status_code, 201, upload.text)
        result = upload.json()
        self.assertEqual(result["status"], "indexed")
        self.assertGreater(result["chunk_count"], 1)
        self.assertEqual(len(result["integrity_hash"]), 64)

        status_response = self.client.get(f"/v1/organizations/{organization_id}/documents/{result['id']}")
        self.assertEqual(status_response.status_code, 200)
        self.assertEqual(status_response.json()["id"], result["id"])

        search = self.client.post(
            f"/v1/organizations/{organization_id}/knowledge/search",
            json={"query": "release note content", "limit": 5},
        )
        self.assertEqual(search.status_code, 200, search.text)
        self.assertGreater(search.json()[0]["relevance_score"], 0)

        investigation = self.client.post(
            f"/v1/organizations/{organization_id}/investigations/preview",
            json={"issue_text": "Client ABC Pharma reports PADER report count mismatch after upgrade to version 26.2. Expected 42, actual 37."},
        )
        self.assertEqual(investigation.status_code, 200, investigation.text)
        investigation_id = investigation.json()["investigation_id"]
        self.assertTrue(investigation_id)
        evidence = investigation.json()["evidence"]
        self.assertTrue(evidence[0]["citations"])
        self.assertEqual(evidence[0]["citations"][0]["source_id"], result["id"])
        self.assertEqual(investigation.json()["extracted_context"]["module"], "Aggregate Reporting")
        quality_checks = {check["name"]: check for check in investigation.json()["quality_checks"]}
        self.assertTrue(quality_checks["evidence_sources_available"]["passed"])
        self.assertFalse(quality_checks["human_review_required"]["passed"])

        history = self.client.get(f"/v1/organizations/{organization_id}/investigations")
        self.assertEqual(history.status_code, 200, history.text)
        record = history.json()["investigations"][0]
        self.assertEqual(record["issue_summary"], investigation.json()["issue_summary"])
        self.assertEqual(record["evidence_source_count"], len(evidence[0]["citations"]))

        other_organization = self.client.post("/v1/organizations", json={"name": f"Other audit team {uuid4()}"})
        other_history = self.client.get(f"/v1/organizations/{other_organization.json()['id']}/investigations")
        self.assertEqual(other_history.status_code, 200)
        self.assertEqual(other_history.json()["investigations"], [])

        feedback = self.client.post(
            f"/v1/organizations/{organization_id}/investigations/{investigation_id}/feedback",
            json={"rating": "helpful", "comment": "Citations were easy to review."},
        )
        self.assertEqual(feedback.status_code, 201, feedback.text)
        self.assertEqual(feedback.json()["rating"], "helpful")
        self.assertEqual(feedback.json()["investigation_id"], investigation_id)

        cross_tenant_feedback = self.client.post(
            f"/v1/organizations/{other_organization.json()['id']}/investigations/{investigation_id}/feedback",
            json={"rating": "needs_review"},
        )
        self.assertEqual(cross_tenant_feedback.status_code, 404)
