# Consulting Intelligence — Public Roadmap

Consulting Intelligence is an evidence-first AI copilot for implementation consultants and support teams. It helps users turn an issue into a structured investigation with relevant knowledge, similar cases, clear unknowns, and reviewable draft communications.

## Product principles

- Evidence before conclusions.
- Human review before external action.
- Clear separation of facts, historical cases, unknowns, and recommendations.
- Build incrementally and validate each release with real user feedback.

## Planned phases

### Phase 1 — Foundation

Establish a runnable local proof of concept with a sample knowledge corpus and a deterministic evidence-pack workflow.

**Public outcome:** a user can submit a sample issue and see structured evidence, citations, unknowns, and suggested next steps.

### Phase 2 — MVP investigation workspace

Add knowledge ingestion, issue analysis, retrieval, similar-case discovery, cited evidence packs, and editable Jira/client-response drafts.

**Public outcome:** a consultant can use approved project knowledge to prepare a reviewable investigation faster.

### Phase 3 — Pilot quality and reliability

Add evaluation scenarios, quality monitoring, error handling, audit visibility, and a controlled pilot feedback loop.

**Public outcome:** a reliable pilot-ready product with measurable answer quality.

### Phase 4 — Integrations and workflow automation

Connect validated workflows to consultant tools such as Jira, email, collaboration, and knowledge systems. Integrations will remain approval-driven.

**Public outcome:** approved work can move cleanly between the investigation workspace and existing team tools.

### Phase 5 — Advanced consulting assistance

Add advanced investigation flows such as release-impact analysis, root-cause assistance, requirements support, and controlled specialist workflows.

**Public outcome:** deeper, repeatable assistance for complex consulting work.

### Phase 6 — Enterprise scale

Expand deployment, administration, governance, and platform capabilities based on validated customer needs.

**Public outcome:** a scalable enterprise-ready offering.

## Release policy

Every completed phase produces a documented release. A release includes:

1. A version number and tagged Git commit.
2. Release notes describing user-visible changes.
3. Setup/run instructions that work from a clean checkout.
4. Tests or verification evidence.
5. Known limitations and the next-phase scope.

See [the release process](docs/release-process.md) and [learning guide](docs/learning-guide.md).
