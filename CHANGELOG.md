# Changelog

All notable public changes are recorded here. Releases follow the process in [docs/release-process.md](docs/release-process.md).

## Unreleased

## v0.4.0 — 2026-09-18

### Added

- Read-only, tenant-scoped Jira handoff preview with explicit approval requirement.
- Internal Jira handoff approval state while keeping external delivery disabled.
- Timestamped internal Jira handoff approval record for reviewer traceability.
- n8n-compatible approved-handoff event preview with network delivery disabled.

## v0.3.0 — 2026-09-18

### Added

- Phase 3 sanitized baseline evaluation suite and API report for expected evidence retrieval.
- Tenant-scoped, read-only investigation audit history in the API and workspace interface.
- Pilot feedback capture for evidence packs, with tenant-scoped investigation validation.
- Visible evidence-pack quality checklist for citations, context completeness, and mandatory human review.
- Privacy-conscious workspace feedback summary for pilot quality monitoring.

## v0.2.0 — 2026-09-18

### Added

- Organization-scoped persistence models for documents, chunks, and investigations.
- A tenant-scope regression test that prevents cross-organization document queries.
- Plain-text document ingestion with SHA-256 integrity hashing, chunking, duplicate detection, and indexed-status API endpoints.
- Browser workflow for creating a workspace and indexing an approved plain-text document.
- Tenant-scoped knowledge-search endpoint with source excerpts, relevance scores, and isolation tests.
- Hybrid retrieval adapter with offline deterministic vectors and optional OpenAI embeddings via environment-based configuration.
- Vector persistence contract: `vector(1536)` on PostgreSQL and JSON vectors for offline SQLite development.
- Organization investigation endpoint that turns retrieved uploaded knowledge into a citation-first evidence pack.
- Deterministic issue-context extraction for client clues, module, version, issue type, and missing information.
- Local ingestion for text-based PDF and DOCX documents, preserving original-file hashes and page or paragraph source locations.
- Controlled evidence source classification for guides, requirements, release notes, SOPs, incidents, historical cases, and RCAs.
- Bounded, documented source-authority ranking and source-type labels on evidence citations.

## v0.1.0 — 2026-09-17

### Added

- Phase 1 investigation interface that renders the fixture-backed evidence pack.
- Public roadmap, release process, and learning guide.
- Local web-to-API connection guidance, browser-safe CORS policy, and preview API tests.
