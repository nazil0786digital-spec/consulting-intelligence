# Consulting Intelligence

Evidence-first investigation copilot for enterprise consulting teams.

The MVP accepts an issue, searches organization-scoped knowledge, and returns a structured evidence pack. It does not execute external actions.

See the [public roadmap](PUBLIC_ROADMAP.md). Detailed architecture and operating plans are intentionally maintained outside the public repository.

## Repository layout

- `apps/web` — Next.js review workspace (to be initialized in Milestone 1)
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
