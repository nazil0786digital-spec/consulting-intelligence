from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Document


def documents_for_organization(session: Session, organization_id: str) -> list[Document]:
    """Retrieve documents only after applying the mandatory tenant scope."""
    statement = select(Document).where(Document.organization_id == organization_id)
    return list(session.scalars(statement))
