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


class InvestigationPreviewRequest(BaseModel):
    organization_id: str = Field(min_length=1, examples=["demo-consulting"])
    issue_text: str = Field(min_length=10, examples=["PADER report results differ after 26.2 upgrade."])


class Citation(BaseModel):
    source_id: str
    title: str
    section: str
    excerpt: str


class EvidenceItem(BaseModel):
    category: Literal["verified_fact", "similar_case", "missing_information", "recommendation"]
    statement: str
    citations: list[Citation] = []


class InvestigationPreviewResult(BaseModel):
    organization_id: str
    issue_summary: str
    extracted_context: dict[str, str | None]
    evidence: list[EvidenceItem]
    jira_draft: str
    client_response_draft: str
    safety_notice: str = "Drafts require human review. This service does not perform external actions."
