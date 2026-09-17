import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import Base
from app.models import Document, Organization
from app.repositories import documents_for_organization
from app.ingestion import content_hash, ingest_text_document


class TenantScopeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        self.first = Organization(name="First consulting team")
        self.second = Organization(name="Second consulting team")
        self.session.add_all([self.first, self.second])
        self.session.flush()
        self.session.add_all(
            [
                Document(organization_id=self.first.id, title="First team's release note", source_type="release_note", integrity_hash="a" * 64),
                Document(organization_id=self.second.id, title="Second team's SOP", source_type="sop", integrity_hash="b" * 64),
            ]
        )
        self.session.commit()

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def test_document_query_returns_only_requested_organization_documents(self) -> None:
        documents = documents_for_organization(self.session, self.first.id)
        self.assertEqual([document.title for document in documents], ["First team's release note"])

    def test_ingestion_hashes_and_chunks_document_content(self) -> None:
        content = b"release note " * 200
        document = ingest_text_document(
            self.session,
            organization_id=self.first.id,
            title="release-notes.txt",
            source_type="release_note",
            content=content,
        )
        self.assertEqual(document.status, "indexed")
        self.assertEqual(document.integrity_hash, content_hash(content))
        self.assertGreater(len(document.chunks), 1)
