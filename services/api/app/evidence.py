from sqlalchemy.orm import Session

from app.contracts import Citation, EvidenceItem, InvestigationPreviewResult
from app.issue_analysis import analyze_issue
from app.models import Investigation
from app.retrieval import search_knowledge


def create_evidence_pack(session: Session, *, organization_id: str, issue_text: str) -> InvestigationPreviewResult:
    context, missing = analyze_issue(issue_text)
    matches = search_knowledge(session, organization_id=organization_id, query=issue_text, limit=5)
    citations = [
        Citation(source_id=document.id, title=document.title, section=chunk.source_locator, excerpt=chunk.content[:600])
        for chunk, document, _score in matches
    ]
    historical = next(
        ((chunk, document) for chunk, document, _score in matches if document.source_type in {"incident", "historical_case", "rca"}),
        None,
    )
    evidence = [
        EvidenceItem(
            category="verified_fact",
            statement=("Retrieved organization knowledge relevant to this issue." if citations else "No approved organization knowledge matched this issue yet."),
            citations=citations,
        ),
        EvidenceItem(
            category="similar_case",
            statement=(f"A related historical source was found: {historical[1].title}." if historical else "No matching historical incident is present in the indexed knowledge."),
            citations=([Citation(source_id=historical[1].id, title=historical[1].title, section=historical[0].source_locator, excerpt=historical[0].content[:600])] if historical else []),
        ),
        EvidenceItem(
            category="missing_information",
            statement=("Confirm " + ", ".join(missing) + " before concluding root cause.") if missing else "The issue includes the core context needed for evidence review; validate it against the cited sources before concluding root cause.",
        ),
        EvidenceItem(
            category="recommendation",
            statement=("Review the cited organization sources and validate the missing context before drafting a conclusion." if citations else "Upload approved requirements, release notes, SOPs, or historical incidents before making a recommendation."),
        ),
    ]
    session.add(
        Investigation(
            organization_id=organization_id,
            issue_text=issue_text,
            status="ready",
            context_json={**context, "missing_information": missing, "evidence_source_ids": [citation.source_id for citation in citations], "retrieval_count": len(citations)},
        )
    )
    session.commit()
    return InvestigationPreviewResult(
        organization_id=organization_id,
        issue_summary=issue_text,
        extracted_context=context,
        evidence=evidence,
        jira_draft="Investigation initiated. The evidence pack identifies approved knowledge sources and the information needed before a conclusion is reached.",
        client_response_draft="Thank you for reporting this issue. We are reviewing the available information and will request any missing details needed to complete the investigation.",
    )
