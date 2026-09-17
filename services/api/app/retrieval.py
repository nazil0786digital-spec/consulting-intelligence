import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.embeddings import EmbeddingProvider, cosine_similarity, get_embedding_provider
from app.models import Document, DocumentChunk


def normalized_terms(text: str) -> set[str]:
    return {term for term in re.findall(r"[a-z0-9]+", text.lower()) if len(term) > 1}


def lexical_relevance(query: str, content: str) -> float:
    """Deterministic Phase 2 baseline; embeddings will augment this score later."""
    query_terms = normalized_terms(query)
    content_terms = normalized_terms(content)
    if not query_terms or not content_terms:
        return 0.0
    return len(query_terms & content_terms) / len(query_terms)


def search_knowledge(
    session: Session,
    *,
    organization_id: str,
    query: str,
    limit: int,
    embedding_provider: EmbeddingProvider | None = None,
) -> list[tuple[DocumentChunk, Document, float]]:
    """Search only records owned by the requested organization."""
    statement = (
        select(DocumentChunk, Document)
        .join(Document, DocumentChunk.document_id == Document.id)
        .where(DocumentChunk.organization_id == organization_id, Document.organization_id == organization_id)
    )
    provider = embedding_provider or get_embedding_provider()
    query_vector = provider.embed(query)
    matches = []
    for chunk, document in session.execute(statement).all():
        lexical_score = lexical_relevance(query, chunk.content)
        vector_score = max(0.0, cosine_similarity(query_vector, provider.embed(chunk.content)))
        # Hybrid scoring retains exact version/module matches while making the vector
        # provider replaceable. Production persists vectors in pgvector at ingestion.
        score = (0.65 * lexical_score) + (0.35 * vector_score)
        matches.append((chunk, document, score))
    return sorted((match for match in matches if match[2] > 0), key=lambda match: match[2], reverse=True)[:limit]
