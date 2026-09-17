import re

from sqlalchemy import select
from sqlalchemy.orm import Session

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


def search_knowledge(session: Session, *, organization_id: str, query: str, limit: int) -> list[tuple[DocumentChunk, Document, float]]:
    """Search only records owned by the requested organization."""
    statement = (
        select(DocumentChunk, Document)
        .join(Document, DocumentChunk.document_id == Document.id)
        .where(DocumentChunk.organization_id == organization_id, Document.organization_id == organization_id)
    )
    matches = [
        (chunk, document, lexical_relevance(query, chunk.content))
        for chunk, document in session.execute(statement).all()
    ]
    return sorted((match for match in matches if match[2] > 0), key=lambda match: match[2], reverse=True)[:limit]
