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

## Working habit

For each delivered feature, we will capture:

- the plain-English explanation;
- the technical explanation;
- one interview/client question and model answer;
- one verification method;
- one trade-off or limitation.
