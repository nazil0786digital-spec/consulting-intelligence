# Consulting Intelligence

Evidence-first investigation copilot for enterprise consulting teams.

The MVP accepts an issue, searches organization-scoped knowledge, and returns a structured evidence pack. It does not execute external actions.

See the [public roadmap](PUBLIC_ROADMAP.md). Detailed architecture and operating plans are intentionally maintained outside the public repository.

## Repository layout

- `apps/web` — Next.js review workspace for the evidence pack
- `services/api` — FastAPI investigation and knowledge APIs
- `services/worker` — asynchronous ingestion/indexing (to be initialized with storage)
- `packages/contracts` — shared API/result contracts
- `fixtures` — sanitized demo knowledge and historical cases
- `docs` — public release process and learning materials

## First runnable slice

From `services/api`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`, or POST to `/v1/investigations/preview` with an `organization_id` and issue text. This fixture-backed endpoint is deliberately deterministic; it establishes the evidence-pack contract before model and database integration.

## Run the web proof of concept

In one terminal, start the API:

```bash
cd services/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

In another terminal, start the interface:

```bash
cd apps/web
cp .env.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`, keep the sample issue, and select **Create evidence pack**. The page calls the local API and renders sourced facts, a similar case, missing information, and a recommendation.

## Verify Phase 1

```bash
cd services/api
python3 -m unittest discover -s tests -v

cd ../../apps/web
npm run build
```

## Phase 2 progress

The API now includes organization-scoped persistence models for documents, document chunks, and investigations. It accepts UTF-8 `.txt` documents, records a SHA-256 integrity hash, creates traceable text chunks, and exposes indexing status. It provides tenant-scoped hybrid retrieval with source locations: a deterministic local vector fallback supports offline development, while an OpenAI embeddings adapter activates only when `OPENAI_API_KEY` is configured. Uploaded knowledge now feeds a citation-first investigation evidence pack. The local default is SQLite for development; PostgreSQL with pgvector persists production embeddings at ingestion. PDF/Word parsing is the next capability.
