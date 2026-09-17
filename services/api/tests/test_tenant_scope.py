import unittest

from sqlalchemy import create_engine
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Session

from app.db import Base
from app.models import Document, DocumentChunk, Organization
from app.repositories import documents_for_organization
from app.ingestion import content_hash, ingest_text_document
from app.retrieval import search_knowledge, source_authority_multiplier
from app.embeddings import DeterministicEmbeddingProvider, cosine_similarity


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
        self.assertEqual(len(document.chunks[0].embedding or []), 1536)

    def test_knowledge_search_returns_relevant_chunks_only_from_the_requested_tenant(self) -> None:
        ingest_text_document(
            self.session,
            organization_id=self.first.id,
            title="Safety report guide",
            source_type="guide",
            content=b"The PADER report requires source population validation after every upgrade.",
        )
        ingest_text_document(
            self.session,
            organization_id=self.second.id,
            title="Private second team guide",
            source_type="guide",
            content=b"The PADER report includes a confidential second-team procedure.",
        )
        matches = search_knowledge(self.session, organization_id=self.first.id, query="PADER source population report", limit=5)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0][1].title, "Safety report guide")

    def test_local_embedding_provider_assigns_higher_similarity_to_related_text(self) -> None:
        provider = DeterministicEmbeddingProvider()
        query = provider.embed("PADER report validation")
        related = cosine_similarity(query, provider.embed("PADER report requires validation"))
        unrelated = cosine_similarity(query, provider.embed("cosmetics shipment palette"))
        self.assertGreater(related, unrelated)

    def test_source_authority_is_bounded_and_prefers_governed_sources(self) -> None:
        self.assertGreater(source_authority_multiplier("requirement"), source_authority_multiplier("document"))
        self.assertGreaterEqual(source_authority_multiplier("document"), 0.9)
        self.assertLessEqual(source_authority_multiplier("requirement"), 1.0)

    def test_postgresql_uses_a_fixed_dimension_vector_column(self) -> None:
        vector_type = DocumentChunk.__table__.c.embedding.type.dialect_impl(postgresql.dialect())
        self.assertEqual(str(vector_type), "VECTOR(1536)")
