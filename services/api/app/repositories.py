from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Document, Investigation, InvestigationFeedback


def documents_for_organization(session: Session, organization_id: str) -> list[Document]:
    """Retrieve documents only after applying the mandatory tenant scope."""
    statement = select(Document).where(Document.organization_id == organization_id)
    return list(session.scalars(statement))


def investigations_for_organization(session: Session, organization_id: str, limit: int = 20) -> list[Investigation]:
    """Read audit history only after applying the mandatory tenant scope."""
    statement = (
        select(Investigation)
        .where(Investigation.organization_id == organization_id)
        .order_by(Investigation.created_at.desc())
        .limit(limit)
    )
    return list(session.scalars(statement))


def feedback_counts_for_organization(session: Session, organization_id: str) -> dict[str, int]:
    statement = (
        select(InvestigationFeedback.rating, func.count(InvestigationFeedback.id))
        .where(InvestigationFeedback.organization_id == organization_id)
        .group_by(InvestigationFeedback.rating)
    )
    counts = {rating: count for rating, count in session.execute(statement).all()}
    return {"helpful": counts.get("helpful", 0), "needs_review": counts.get("needs_review", 0)}
