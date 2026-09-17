from typing import Literal
from pydantic import BaseModel, Field


class OrganizationCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=160, examples=["Acme Consulting"])


class OrganizationResponse(BaseModel):
    id: str
    name: str


class DocumentResponse(BaseModel):
    id: str
    organization_id: str
    title: str
    source_type: str
    status: str
    integrity_hash: str
    chunk_count: int


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=2_000)
    limit: int = Field(default=5, ge=1, le=10)


class KnowledgeSearchResult(BaseModel):
    chunk_id: str
    document_id: str
    document_title: str
    source_type: str
    source_locator: str
    excerpt: str
    relevance_score: float


class OrganizationInvestigationRequest(BaseModel):
    issue_text: str = Field(min_length=10, max_length=10_000)


class InvestigationPreviewRequest(BaseModel):
    organization_id: str = Field(min_length=1, examples=["demo-consulting"])
    issue_text: str = Field(min_length=10, examples=["PADER report results differ after 26.2 upgrade."])


class Citation(BaseModel):
    source_id: str
    title: str
    source_type: str
    section: str
    excerpt: str


class EvidenceItem(BaseModel):
    category: Literal["verified_fact", "similar_case", "missing_information", "recommendation"]
    statement: str
    citations: list[Citation] = []


class InvestigationPreviewResult(BaseModel):
    organization_id: str
    investigation_id: str | None = None
    issue_summary: str
    extracted_context: dict[str, str | None]
    evidence: list[EvidenceItem]
    jira_draft: str
    client_response_draft: str
    quality_checks: list["QualityCheck"] = []
    safety_notice: str = "Drafts require human review. This service does not perform external actions."


class QualityCheck(BaseModel):
    name: str
    passed: bool
    detail: str


class EvaluationCaseResult(BaseModel):
    scenario_id: str
    passed: bool
    checks: dict[str, bool]
    detail: str


class EvaluationReport(BaseModel):
    suite: str
    total_cases: int
    passed_cases: int
    results: list[EvaluationCaseResult]


class InvestigationAuditRecord(BaseModel):
    id: str
    issue_summary: str
    status: str
    created_at: str
    evidence_source_count: int


class InvestigationAuditList(BaseModel):
    organization_id: str
    investigations: list[InvestigationAuditRecord]


class InvestigationFeedbackRequest(BaseModel):
    rating: Literal["helpful", "needs_review"]
    comment: str | None = Field(default=None, max_length=2_000)


class InvestigationFeedbackResponse(BaseModel):
    id: str
    investigation_id: str
    rating: str
    comment: str | None
    created_at: str


class FeedbackSummary(BaseModel):
    organization_id: str
    helpful_count: int
    needs_review_count: int
    total_count: int


class IntegrationHandoffPreview(BaseModel):
    integration: Literal["jira"]
    mode: Literal["preview_only"]
    approval_required: bool
    investigation_id: str
    payload: dict[str, str | list[str]]
