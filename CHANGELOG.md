# Changelog

All notable public changes are recorded here. Releases follow the process in [docs/release-process.md](docs/release-process.md).

## Unreleased

### Added

- Organization-scoped persistence models for documents, chunks, and investigations.
- A tenant-scope regression test that prevents cross-organization document queries.
- Plain-text document ingestion with SHA-256 integrity hashing, chunking, duplicate detection, and indexed-status API endpoints.
- Browser workflow for creating a workspace and indexing an approved plain-text document.
- Tenant-scoped knowledge-search endpoint with source excerpts, relevance scores, and isolation tests.
- Hybrid retrieval adapter with offline deterministic vectors and optional OpenAI embeddings via environment-based configuration.
- Vector persistence contract: `vector(1536)` on PostgreSQL and JSON vectors for offline SQLite development.

## v0.1.0 — 2026-09-17

### Added

- Phase 1 investigation interface that renders the fixture-backed evidence pack.
- Public roadmap, release process, and learning guide.
- Local web-to-API connection guidance, browser-safe CORS policy, and preview API tests.
