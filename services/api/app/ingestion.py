import hashlib
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Document, DocumentChunk


MAX_DOCUMENT_BYTES = 1_000_000
CHUNK_WORDS = 180


def content_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def chunk_text(text: str, words_per_chunk: int = CHUNK_WORDS) -> list[str]:
    """Create stable, readable chunks for the first ingestion release."""
    words = re.findall(r"\S+", text)
    return [" ".join(words[index : index + words_per_chunk]) for index in range(0, len(words), words_per_chunk)]


def ingest_text_document(
    session: Session,
    *,
    organization_id: str,
    title: str,
    source_type: str,
    content: bytes,
) -> Document:
    if not content:
        raise ValueError("The uploaded document is empty.")
    if len(content) > MAX_DOCUMENT_BYTES:
        raise ValueError("The uploaded document exceeds the 1 MB Phase 2 limit.")
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("Only UTF-8 plain-text documents are supported in this release.") from error

    digest = content_hash(content)
    duplicate = session.scalar(
        select(Document).where(
            Document.organization_id == organization_id,
            Document.integrity_hash == digest,
        )
    )
    if duplicate:
        raise ValueError("This exact document has already been indexed for the organization.")

    chunks = chunk_text(text)
    if not chunks:
        raise ValueError("The uploaded document contains no indexable text.")

    document = Document(
        organization_id=organization_id,
        title=title,
        source_type=source_type,
        status="processing",
        integrity_hash=digest,
        metadata_json={"encoding": "utf-8", "bytes": len(content)},
    )
    session.add(document)
    session.flush()
    session.add_all(
        [
            DocumentChunk(
                organization_id=organization_id,
                document_id=document.id,
                content=chunk,
                source_locator=f"chunk:{index + 1}",
                metadata_json={"chunk_index": index, "word_count": len(chunk.split())},
            )
            for index, chunk in enumerate(chunks)
        ]
    )
    document.status = "indexed"
    session.commit()
    session.refresh(document)
    return document
