# Learning Guide

This project is also a hands-on AI Solutions Engineering curriculum. Each feature is built with an explanation of the problem, design choice, implementation, verification, and trade-off.

## The answer framework

When explaining a solution to an interviewer, client, or teammate, use this sequence:

1. **Problem:** What repetitive or risky consulting task are we solving?
2. **Workflow:** What happens from issue intake to human decision?
3. **Data:** Which approved sources are searched and how are they scoped?
4. **AI:** What does the model do, and what must it not decide?
5. **Trust:** How do citations, review, and testing limit unsupported output?
6. **Integration:** Which system receives the approved result, if any?
7. **Measurement:** How do we measure time saved, retrieval quality, and reliability?

## Phase learning goals

| Phase | You will be able to explain |
|---|---|
| 1 | APIs, RAG basics, embeddings, vector search, citations, and source integrity hashes |
| 2 | Multi-tenant data, ingestion, metadata filters, structured outputs, and human-in-the-loop review |
| 3 | Evaluation, observability, audits, authentication, authorization, encryption, and reliability |
| 4 | APIs, webhooks, n8n, MCP, approval-driven integrations, and credential governance |
| 5 | Agent orchestration, LangGraph, controlled tools, guardrails, and read-only data investigation |
| 6 | Enterprise deployment, SSO, scaling, governance, cost control, and product metrics |

## Phase 3 baseline evaluation

**Plain English:** before showing the product to pilot users, we keep a small set of sanitized example issues and check that the expected evidence sources are still returned after a change.

**Technical:** `GET /v1/evaluations/baseline` runs version-controlled fixture scenarios and reports the pass/fail result for each one. It never reads customer workspace data, so the quality baseline is reproducible and safe to publish.

**Interview answer:** “We evaluate retrieval with curated cases that define expected citations. We version the cases with the code, run them in CI, and keep customer data out of the baseline suite.”

**Trade-off:** this is a small regression baseline, not a substitute for pilot-user feedback or a broader labeled evaluation set.

## Phase 3 investigation audit history

**Plain English:** a reviewer can see what investigations were created in their workspace, when they ran, and how many evidence sources each used.

**Technical:** the read-only history endpoint filters records by organization before returning minimal audit metadata. The interface loads it only after an investigation is created.

**Interview answer:** “We begin auditability with a tenant-scoped, read-only event view. It gives pilot reviewers traceability without granting the product permission to change tickets, documents, or client systems.”

## Phase 3 pilot feedback

**Plain English:** after reviewing an evidence pack, a pilot user can say whether it was helpful or needs review, with an optional note.

**Technical:** feedback is stored against the investigation and organization, and the API rejects attempts to submit feedback for an investigation in another workspace.

**Trade-off:** feedback is a quality signal, not an approval. Authentication and reviewer identity are planned before broader deployment.

## Phase 3 feedback monitoring

**Plain English:** the workspace turns pilot feedback into simple aggregate counts so the team can see whether evidence packs are generally useful or often need review.

**Technical:** the summary endpoint aggregates only rating categories inside the workspace. It intentionally does not return free-text feedback comments to the dashboard.

**Interview answer:** “We measure pilot quality using workspace-scoped aggregates. We separate operational metrics from free-text feedback to reduce unnecessary data exposure.”

## Phase 3 quality checklist

**Plain English:** every evidence pack tells the reviewer if it found approved sources, whether key context is still missing, and that a human review is mandatory.

**Technical:** quality checks are deterministic rules returned with the result. A failed check is a reviewer signal, not a silent fallback or an automated decision.

**Interview answer:** “We turn quality expectations into visible, testable checks. The UI does not hide uncertainty; it tells the consultant exactly what still needs review.”

## Phase 4 Jira handoff preview

**Plain English:** the product prepares a proposed Jira ticket, but a consultant must review it before anything can be created externally.

**Technical:** the handoff endpoint is read-only. It builds a tenant-scoped preview from the saved investigation and marks the payload `preview_only` with `approval_required: true`.

**Interview answer:** “We begin integrations with a dry-run payload. That lets us validate field mapping and human approval before storing credentials or permitting an external write.”

**Trade-off:** this preview does not create a Jira issue. A future approved integration will need authentication, explicit approval state, and an audit event for the external action.

## Phase 4 approval state

**Plain English:** a consultant can approve the prepared handoff inside the workspace, but approval alone never sends it anywhere.

**Technical:** approval is a tenant-scoped state on the saved investigation. The handoff API remains `preview_only`; an external delivery capability does not exist.

**Interview answer:** “We model approval separately from execution. That gives the workflow a clear control point and prevents an integration preview from becoming an accidental external write.”

**Audit note:** this early approval record stores a timestamp but not reviewer identity. Identity-bound approvals require authentication before external delivery is enabled.

## Working habit

For each delivered feature, we will capture:

- the plain-English explanation;
- the technical explanation;
- one interview/client question and model answer;
- one verification method;
- one trade-off or limitation.
