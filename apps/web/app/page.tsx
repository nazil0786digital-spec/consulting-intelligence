"use client";

import { ChangeEvent, FormEvent, useState } from "react";

type Citation = { source_id: string; title: string; section: string; excerpt: string };
type Evidence = { category: string; statement: string; citations: Citation[] };
type Result = {
  issue_summary: string;
  extracted_context: Record<string, string | null>;
  evidence: Evidence[];
  jira_draft: string;
  client_response_draft: string;
  safety_notice: string;
};

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
  const [ingestionError, setIngestionError] = useState<string | null>(null);
  const [creatingWorkspace, setCreatingWorkspace] = useState(false);
  const [uploading, setUploading] = useState(false);

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
      formData.set("source_type", "document");
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
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unexpected error");
    } finally {
      setLoading(false);
    }
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
          <label htmlFor="document">Approved UTF-8 text document</label>
          <input id="document" type="file" accept=".txt,text/plain" onChange={chooseDocument} required />
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
            <strong>{citation.title}</strong> · {citation.section}<br />
            {citation.excerpt}
          </blockquote>)}
        </article>)}

        <section className="two-column">
          <article className="card"><p className="eyebrow">Draft Jira update</p><p>{result.jira_draft}</p></article>
          <article className="card"><p className="eyebrow">Draft client response</p><p>{result.client_response_draft}</p></article>
        </section>
        <p className="notice">{result.safety_notice}</p>
      </section>}
    </main>
  );
}
