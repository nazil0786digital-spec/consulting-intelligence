from fastapi import FastAPI, HTTPException

from app.contracts import EvidenceItem, InvestigationPreviewRequest, InvestigationPreviewResult
from app.fixtures import DEMO_ORGANIZATION, citations_for

app = FastAPI(title="Consulting Intelligence API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "fixture-backed"}


@app.post("/v1/investigations/preview", response_model=InvestigationPreviewResult)
def preview_investigation(request: InvestigationPreviewRequest) -> InvestigationPreviewResult:
    # The fixture endpoint refuses unknown tenants. Production retrieval must apply this
    # organization scope in the database, vector store, and object storage layers.
    if request.organization_id != DEMO_ORGANIZATION:
        raise HTTPException(status_code=404, detail="Organization has no approved fixture corpus")

    citations = citations_for(request.issue_text)
    summary = request.issue_text.strip()
    facts = [
        EvidenceItem(
            category="verified_fact",
            statement="The approved release notes describe a possible post-upgrade count difference when legacy inclusion rules remain enabled.",
            citations=[citations[0]],
        ),
        EvidenceItem(
            category="similar_case",
            statement="A prior incident with a post-upgrade count mismatch was resolved by correcting a legacy inclusion-rule setting and rerunning the report.",
            citations=[citations[1]],
        ),
        EvidenceItem(
            category="missing_information",
            statement="Collect the report configuration, execution details, source-population count, and relevant logs before confirming a root cause.",
        ),
        EvidenceItem(
            category="recommendation",
            statement="Compare the current inclusion rules to the 26.2 configuration guidance, validate the source population, then rerun the report in a controlled review.",
        ),
    ]
    return InvestigationPreviewResult(
        organization_id=request.organization_id,
        issue_summary=summary,
        extracted_context={"client": None, "product": "Aggregate Reporting", "module": "Reporting", "version": "26.2", "issue_type": "possible configuration or upgrade issue"},
        evidence=facts,
        jira_draft="Investigation initiated. We identified release-note guidance and a similar historical case involving legacy inclusion rules after an upgrade. Next, we will validate report configuration and source-population details before concluding root cause.",
        client_response_draft="Thank you for reporting the discrepancy. We are reviewing the report configuration and source data against the post-upgrade guidance. To continue, please share the report configuration, execution details, and any relevant logs.",
    )
