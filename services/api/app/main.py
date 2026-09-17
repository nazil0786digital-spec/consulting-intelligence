from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.contracts import DocumentResponse, EvidenceItem, InvestigationPreviewRequest, InvestigationPreviewResult, OrganizationCreateRequest, OrganizationResponse
from app.db import Base, engine, get_session
from app.fixtures import DEMO_ORGANIZATION, citations_for
from app.ingestion import ingest_text_document
from app.models import Document, Organization

# Import models before table setup so local development has the complete metadata.
from app import models  # noqa: F401

app = FastAPI(title="Consulting Intelligence API", version="0.1.0")

# Phase 1 runs the web UI and API on different local ports. CORS permits only the
# local UI origin; production will replace this with configured trusted origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.on_event("startup")
def create_local_tables() -> None:
    """Temporary Phase 2 local setup; production will use reviewed migrations."""
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "fixture-backed"}


@app.post("/v1/organizations", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(request: OrganizationCreateRequest, session: Session = Depends(get_session)) -> OrganizationResponse:
    organization = Organization(name=request.name)
    session.add(organization)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=409, detail="An organization with that name already exists.") from error
    session.refresh(organization)
    return OrganizationResponse(id=organization.id, name=organization.name)


@app.post("/v1/organizations/{organization_id}/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    organization_id: str,
    file: UploadFile = File(...),
    source_type: str = Form("document"),
    session: Session = Depends(get_session),
) -> DocumentResponse:
    if not session.get(Organization, organization_id):
        raise HTTPException(status_code=404, detail="Organization not found.")
    if file.content_type not in {"text/plain", "application/octet-stream"}:
        raise HTTPException(status_code=415, detail="Phase 2 currently accepts plain-text files only.")
    content = await file.read()
    try:
        document = ingest_text_document(
            session,
            organization_id=organization_id,
            title=file.filename or "untitled.txt",
            source_type=source_type,
            content=content,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    chunk_count = len(document.chunks)
    return DocumentResponse(
        id=document.id,
        organization_id=document.organization_id,
        title=document.title,
        source_type=document.source_type,
        status=document.status,
        integrity_hash=document.integrity_hash,
        chunk_count=chunk_count,
    )


@app.get("/v1/organizations/{organization_id}/documents/{document_id}", response_model=DocumentResponse)
def document_status(organization_id: str, document_id: str, session: Session = Depends(get_session)) -> DocumentResponse:
    document = session.get(Document, document_id)
    if not document or document.organization_id != organization_id:
        raise HTTPException(status_code=404, detail="Document not found.")
    return DocumentResponse(
        id=document.id,
        organization_id=document.organization_id,
        title=document.title,
        source_type=document.source_type,
        status=document.status,
        integrity_hash=document.integrity_hash,
        chunk_count=len(document.chunks),
    )


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
