"use client";

import { ChangeEvent, FormEvent, useState } from "react";

type Citation = { source_id: string; title: string; source_type: string; section: string; excerpt: string };
type Evidence = { category: string; statement: string; citations: Citation[] };
type Result = {
  investigation_id: string | null;
  issue_summary: string;
  extracted_context: Record<string, string | null>;
  evidence: Evidence[];
  jira_draft: string;
  client_response_draft: string;
  safety_notice: string;
};
type AuditRecord = { id: string; issue_summary: string; status: string; created_at: string; evidence_source_count: number };

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
const initialIssue = "PADER report counts differ after an upgrade to version 26.2.";

const labels: Record<string, string> = {
  verified_fact: "Verified information",
  similar_case: "Similar historical case",
  missing_information: "Missing information",
  recommendation: "Recommended next step"
};

export default function Home() {
  const [issue, setIssue] = useState(initialIssue);
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [workspaceName, setWorkspaceName] = useState("");
  const [organizationId, setOrganizationId] = useState<string | null>(null);
  const [documentFile, setDocumentFile] = useState<File | null>(null);
  const [documentStatus, setDocumentStatus] = useState<string | null>(null);
  const [sourceType, setSourceType] = useState("document");
  const [ingestionError, setIngestionError] = useState<string | null>(null);
  const [creatingWorkspace, setCreatingWorkspace] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [auditHistory, setAuditHistory] = useState<AuditRecord[]>([]);
  const [feedbackComment, setFeedbackComment] = useState("");
  const [feedbackStatus, setFeedbackStatus] = useState<string | null>(null);

  async function refreshAuditHistory(workspaceId: string) {
    const response = await fetch(`${API_URL}/v1/organizations/${workspaceId}/investigations`);
    if (response.ok) setAuditHistory((await response.json()).investigations);
  }

  async function createWorkspace(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setCreatingWorkspace(true);
    setIngestionError(null);
    try {
      const response = await fetch(`${API_URL}/v1/organizations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: workspaceName })
      });
      if (!response.ok) throw new Error("The workspace could not be created. Try another name.");
      const workspace = await response.json();
      setOrganizationId(workspace.id);
      setDocumentStatus(`Workspace “${workspace.name}” is ready for approved knowledge.`);
    } catch (reason) {
      setIngestionError(reason instanceof Error ? reason.message : "Unexpected error");
    } finally {
      setCreatingWorkspace(false);
    }
  }

  function chooseDocument(event: ChangeEvent<HTMLInputElement>) {
    setDocumentFile(event.target.files?.[0] ?? null);
    setDocumentStatus(null);
    setIngestionError(null);
  }

  async function uploadDocument(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!organizationId || !documentFile) return;
    setUploading(true);
    setIngestionError(null);
    try {
      const formData = new FormData();
      formData.set("file", documentFile);
      formData.set("source_type", sourceType);
      const response = await fetch(`${API_URL}/v1/organizations/${organizationId}/documents`, { method: "POST", body: formData });
      if (!response.ok) {
        const detail = await response.json().catch(() => null);
        throw new Error(detail?.detail ?? "The document could not be indexed.");
      }
      const document = await response.json();
      setDocumentStatus(`${document.title} indexed: ${document.chunk_count} traceable chunks, SHA-256 ${document.integrity_hash.slice(0, 12)}…`);
    } catch (reason) {
      setIngestionError(reason instanceof Error ? reason.message : "Unexpected error");
    } finally {
      setUploading(false);
    }
  }

  async function investigate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const endpoint = organizationId
        ? `${API_URL}/v1/organizations/${organizationId}/investigations/preview`
        : `${API_URL}/v1/investigations/preview`;
      const payload = organizationId
        ? { issue_text: issue }
        : { organization_id: "demo-consulting", issue_text: issue };
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (!response.ok) throw new Error("The investigation could not be created. Check that the API is running.");
      setResult(await response.json());
      setFeedbackComment("");
      setFeedbackStatus(null);
      if (organizationId) await refreshAuditHistory(organizationId);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unexpected error");
    } finally {
      setLoading(false);
    }
  }

  async function submitFeedback(rating: "helpful" | "needs_review") {
    if (!organizationId || !result?.investigation_id) return;
    setFeedbackStatus("Saving feedback…");
    const response = await fetch(`${API_URL}/v1/organizations/${organizationId}/investigations/${result.investigation_id}/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rating, comment: feedbackComment || null })
    });
    setFeedbackStatus(response.ok ? "Feedback saved for pilot review." : "Feedback could not be saved.");
  }

  return (
    <main>
      <header>
        <p className="eyebrow">Phase 1 proof of concept</p>
        <h1>Consulting Intelligence</h1>
        <p>Turn a consulting issue into evidence, unknowns, and a reviewable next step.</p>
      </header>

      <section className="card">
        <p className="eyebrow">Phase 2 knowledge workspace</p>
        <h2>Prepare approved knowledge</h2>
        {!organizationId ? <form onSubmit={createWorkspace}>
          <label htmlFor="workspace">Workspace name</label>
          <input id="workspace" value={workspaceName} onChange={(event) => setWorkspaceName(event.target.value)} minLength={2} maxLength={160} required placeholder="Example Consulting Team" />
          <button disabled={creatingWorkspace}>{creatingWorkspace ? "Creating…" : "Create workspace"}</button>
        </form> : <form onSubmit={uploadDocument}>
          <label htmlFor="document">Approved document</label>
          <input id="document" type="file" accept=".txt,.pdf,.docx,text/plain,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document" onChange={chooseDocument} required />
          <p className="hint">Supported: UTF-8 text, text-based PDF, and DOCX. Scanned PDFs require OCR and are not supported yet.</p>
          <label htmlFor="sourceType">Evidence source type</label>
          <select id="sourceType" value={sourceType} onChange={(event) => setSourceType(event.target.value)}>
            <option value="document">General document</option>
            <option value="guide">Product or process guide</option>
            <option value="requirement">Requirement</option>
            <option value="release_note">Release note</option>
            <option value="sop">Standard operating procedure</option>
            <option value="incident">Incident</option>
            <option value="historical_case">Historical case</option>
            <option value="rca">Root-cause analysis</option>
          </select>
          <button disabled={!documentFile || uploading}>{uploading ? "Indexing…" : "Index document"}</button>
        </form>}
        {documentStatus && <p className="notice success">{documentStatus}</p>}
        {ingestionError && <p className="error">{ingestionError}</p>}
      </section>

      <section className="card">
        <h2>New investigation</h2>
        <p className="hint">{organizationId ? "This investigation searches the knowledge indexed in your workspace." : "Create a workspace and index a document above to investigate your own knowledge; otherwise this uses the sample corpus."}</p>
        <form onSubmit={investigate}>
          <label htmlFor="issue">Client issue, email, or ticket</label>
          <textarea id="issue" value={issue} onChange={(event) => setIssue(event.target.value)} minLength={10} required />
          <button disabled={loading}>{loading ? "Investigating…" : "Create evidence pack"}</button>
        </form>
        {error && <p className="error">{error}</p>}
      </section>

      {organizationId && auditHistory.length > 0 && <section className="card">
        <p className="eyebrow">Phase 3 audit visibility</p>
        <h2>Recent investigations</h2>
        <p className="hint">Read-only workspace history. External actions are not available.</p>
        <ul className="audit-list">
          {auditHistory.map((record) => <li key={record.id}>
            <strong>{record.issue_summary}</strong><br />
            {record.status} · {record.evidence_source_count} cited source{record.evidence_source_count === 1 ? "" : "s"} · {new Date(record.created_at).toLocaleString()}
          </li>)}
        </ul>
      </section>}

      {result && <section className="results" aria-live="polite">
        <div className="card">
          <p className="eyebrow">Issue summary</p>
          <h2>{result.issue_summary}</h2>
          <dl>
            {Object.entries(result.extracted_context).map(([key, value]) => <div key={key}><dt>{key.replaceAll("_", " ")}</dt><dd>{value ?? "Not identified"}</dd></div>)}
          </dl>
        </div>

        {result.evidence.map((item, index) => <article className="card" key={`${item.category}-${index}`}>
          <p className="eyebrow">{labels[item.category] ?? item.category}</p>
          <p>{item.statement}</p>
          {item.citations.map((citation) => <blockquote key={citation.source_id}>
            <strong>{citation.title}</strong> · {citation.source_type.replaceAll("_", " ")} · {citation.section}<br />
            {citation.excerpt}
          </blockquote>)}
        </article>)}

        <section className="two-column">
          <article className="card"><p className="eyebrow">Draft Jira update</p><p>{result.jira_draft}</p></article>
          <article className="card"><p className="eyebrow">Draft client response</p><p>{result.client_response_draft}</p></article>
        </section>
        {organizationId && result.investigation_id && <section className="card">
          <p className="eyebrow">Pilot feedback</p>
          <h2>Was this evidence pack useful?</h2>
          <textarea aria-label="Feedback comment" value={feedbackComment} onChange={(event) => setFeedbackComment(event.target.value)} maxLength={2000} placeholder="Optional: what should improve?" />
          <div className="feedback-actions">
            <button type="button" onClick={() => submitFeedback("helpful")}>Helpful</button>
            <button type="button" className="secondary" onClick={() => submitFeedback("needs_review")}>Needs review</button>
          </div>
          {feedbackStatus && <p className="notice">{feedbackStatus}</p>}
        </section>}
        <p className="notice">{result.safety_notice}</p>
      </section>}
    </main>
  );
}
