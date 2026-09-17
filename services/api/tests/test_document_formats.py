from io import BytesIO
import unittest
from uuid import uuid4

from docx import Document as WordDocument
from fastapi.testclient import TestClient

from app.main import app


def text_pdf(text: str) -> bytes:
    """Build a small, valid text PDF without a production-only test dependency."""
    objects = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        f"<< /Length {len(f'BT /F1 12 Tf 72 720 Td ({text}) Tj ET')} >>\nstream\nBT /F1 12 Tf 72 720 Td ({text}) Tj ET\nendstream",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    body = "%PDF-1.4\n"
    offsets = [0]
    for index, value in enumerate(objects, start=1):
        offsets.append(len(body.encode()))
        body += f"{index} 0 obj\n{value}\nendobj\n"
    xref = len(body.encode())
    body += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n"
    body += "".join(f"{offset:010} 00000 n \n" for offset in offsets[1:])
    return (body + f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n").encode()


def word_document_bytes(text: str) -> bytes:
    document = WordDocument()
    document.add_paragraph(text)
    stream = BytesIO()
    document.save(stream)
    return stream.getvalue()


class DocumentFormatTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.client.__enter__()
        organization = self.client.post("/v1/organizations", json={"name": f"Format test {uuid4()}"})
        self.organization_id = organization.json()["id"]

    def tearDown(self) -> None:
        self.client.__exit__(None, None, None)

    def test_indexes_text_pdf_with_page_citation_locator(self) -> None:
        response = self.client.post(
            f"/v1/organizations/{self.organization_id}/documents",
            files={"file": ("release-note.pdf", text_pdf("PADER configuration guidance"), "application/pdf")},
        )
        self.assertEqual(response.status_code, 201, response.text)
        search = self.client.post(f"/v1/organizations/{self.organization_id}/knowledge/search", json={"query": "PADER guidance"})
        self.assertEqual(search.status_code, 200, search.text)
        self.assertEqual(search.json()[0]["source_locator"], "page:1")

    def test_indexes_docx_with_paragraph_citation_locator(self) -> None:
        response = self.client.post(
            f"/v1/organizations/{self.organization_id}/documents",
            files={
                "file": (
                    "investigation.docx",
                    word_document_bytes("Client configuration review and expected report count."),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )
        self.assertEqual(response.status_code, 201, response.text)
        search = self.client.post(f"/v1/organizations/{self.organization_id}/knowledge/search", json={"query": "configuration report"})
        self.assertEqual(search.status_code, 200, search.text)
        self.assertEqual(search.json()[0]["source_locator"], "paragraph:1")
