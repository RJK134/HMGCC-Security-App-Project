/** Typed API client for the SRA backend. */

import type {
  Conversation,
  ConversationListItem,
  DocumentMetadata,
  HealthStatus,
  PinnedFact,
  Project,
  QueryRequest,
  QueryResponse,
  SourceTier,
  Citation,
} from "../types";

// Use relative URL so it works via Vite proxy from any device on the network
const API_BASE = "/api/v1";
const TIMEOUT_MS = 30_000;

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: Record<string, unknown>,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), TIMEOUT_MS);

  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new ApiError(
        body.message || `Request failed: ${res.status}`,
        res.status,
        body.details,
      );
    }

    return res.json() as Promise<T>;
  } finally {
    clearTimeout(timeout);
  }
}

// --- Health ---
export async function healthCheck(): Promise<HealthStatus> {
  return request<HealthStatus>("/health");
}

// --- Projects ---
export async function listProjects(): Promise<Project[]> {
  const res = await request<{ projects: Project[] }>("/projects");
  // Backend doesn't have this endpoint yet — fallback
  return res?.projects ?? [];
}

export async function createProject(data: {
  name: string;
  description?: string;
}): Promise<Project> {
  const res = await request<{ project: Project }>("/projects", {
    method: "POST",
    body: JSON.stringify(data),
  });
  return res.project;
}

export async function getProject(id: string): Promise<Project> {
  return request<Project>(`/projects/${id}`);
}

export async function deleteProject(id: string): Promise<void> {
  await request(`/projects/${id}`, { method: "DELETE" });
}

// --- Documents ---
export async function listDocuments(
  projectId: string,
  limit = 50,
  offset = 0,
): Promise<{ documents: DocumentMetadata[]; total: number }> {
  return request(`/documents?project_id=${projectId}&limit=${limit}&offset=${offset}`);
}

export async function getDocument(
  id: string,
): Promise<{ document: DocumentMetadata; chunk_count: number; sample_chunks: unknown[] }> {
  return request(`/documents/${id}`);
}

export async function uploadDocument(
  projectId: string,
  file: File,
  tier?: SourceTier,
): Promise<DocumentMetadata> {
  const form = new FormData();
  form.append("file", file);
  form.append("project_id", projectId);
  if (tier) form.append("source_tier", tier);

  const controller = new AbortController();
  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: "POST",
    body: form,
    signal: controller.signal,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(body.message || "Upload failed", res.status);
  }

  const data = await res.json();
  return data.document;
}

export async function deleteDocument(id: string): Promise<void> {
  await request(`/documents/${id}`, { method: "DELETE" });
}

export async function updateDocumentTier(
  id: string,
  tier: SourceTier,
): Promise<DocumentMetadata> {
  const res = await request<{ document: DocumentMetadata }>(
    `/documents/${id}/tier`,
    { method: "PATCH", body: JSON.stringify({ tier }) },
  );
  return res.document;
}

// --- Query ---
export function queryStream(req: QueryRequest): EventSource {
  const url = `${API_BASE}/query?stream=true`;
  // EventSource only supports GET, so we use fetch with SSE parsing
  // Return a custom EventSource-like object
  const es = new EventSource(url); // Placeholder — real SSE needs POST
  return es;
}

export async function querySimple(req: QueryRequest): Promise<QueryResponse> {
  return request<QueryResponse>("/query/simple", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export async function queryPost(
  req: QueryRequest,
): Promise<Response> {
  return fetch(`${API_BASE}/query?stream=true`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
}

// --- Conversations ---
export async function listConversations(
  projectId: string,
): Promise<ConversationListItem[]> {
  const res = await request<{ conversations: ConversationListItem[] }>(
    `/conversations?project_id=${projectId}`,
  );
  return res.conversations;
}

export async function getConversation(id: string): Promise<{
  conversation: Conversation;
  messages: unknown[];
  pinned_facts: unknown[];
}> {
  return request(`/conversations/${id}`);
}

export async function createConversation(
  projectId: string,
  title: string,
): Promise<Conversation> {
  const res = await request<{ conversation: Conversation }>("/conversations", {
    method: "POST",
    body: JSON.stringify({ project_id: projectId, title }),
  });
  return res.conversation;
}

export async function deleteConversation(id: string): Promise<void> {
  await request(`/conversations/${id}`, { method: "DELETE" });
}

export async function renameConversation(
  id: string,
  title: string,
): Promise<void> {
  await request(`/conversations/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ title }),
  });
}

// --- Pinned Facts ---
export async function pinFact(
  conversationId: string,
  content: string,
  sourceRefs: Citation[] = [],
): Promise<PinnedFact> {
  const res = await request<{ pinned_fact: PinnedFact }>(
    `/conversations/${conversationId}/pin`,
    { method: "POST", body: JSON.stringify({ content, source_refs: sourceRefs }) },
  );
  return res.pinned_fact;
}

export async function getPins(conversationId: string): Promise<PinnedFact[]> {
  const res = await request<{ pinned_facts: PinnedFact[] }>(
    `/conversations/${conversationId}/pins`,
  );
  return res.pinned_facts;
}

export async function unpinFact(
  conversationId: string,
  factId: string,
): Promise<void> {
  await request(`/conversations/${conversationId}/pins/${factId}`, {
    method: "DELETE",
  });
}

// --- Models ---
export async function listModels(): Promise<string[]> {
  const health = await healthCheck();
  return health.available_models;
}
