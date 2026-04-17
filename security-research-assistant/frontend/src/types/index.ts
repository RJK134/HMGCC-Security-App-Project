/** TypeScript types mirroring backend Pydantic models. */

export type DocumentType = "pdf" | "image" | "code" | "text" | "spreadsheet" | "schematic";

export type SourceTier =
  | "tier_1_manufacturer"
  | "tier_2_academic"
  | "tier_3_trusted_forum"
  | "tier_4_unverified";

export type DocumentStatus = "pending" | "processing" | "indexed" | "failed";
export type MessageRole = "user" | "assistant" | "system";

export interface Project {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
  document_count: number;
  conversation_count: number;
}

export interface DocumentMetadata {
  id: string;
  project_id: string;
  filename: string;
  filepath: string;
  filetype: DocumentType;
  size_bytes: number;
  status: DocumentStatus;
  source_tier: SourceTier;
  import_timestamp: string;
  page_count: number | null;
  metadata: Record<string, unknown>;
}

export interface Citation {
  document_id: string;
  document_name: string;
  page_number: number | null;
  chunk_id: string;
  relevance_score: number;
  excerpt: string;
  source_tier?: SourceTier | null;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: MessageRole;
  content: string;
  citations: Citation[];
  confidence_score: number | null;
  created_at: string;
}

export interface PinnedFact {
  id: string;
  conversation_id: string;
  content: string;
  source_refs: Citation[];
  created_at: string;
}

export interface Conversation {
  id: string;
  project_id: string;
  title: string;
  summary: string | null;
  messages: Message[];
  pinned_facts: PinnedFact[];
  created_at: string;
  updated_at: string;
}

export interface ConversationListItem {
  id: string;
  title: string;
  summary: string | null;
  message_count: number;
  last_message_preview: string;
  created_at: string;
  updated_at: string;
}

export interface ConfidenceResult {
  score: number;
  explanation: string;
  flagged_claims: string[];
  alternative_interpretations: string[];
}

export interface QueryRequest {
  question: string;
  project_id: string;
  conversation_id?: string;
}

export interface QueryResponse {
  answer: string;
  citations: Citation[];
  confidence: ConfidenceResult;
  sources_used: number;
  retrieval_scores: Record<string, number>;
  conversation_id?: string;
}

export interface HealthStatus {
  status: "ok" | "degraded" | "error";
  ollama_connected: boolean;
  available_models: string[];
  database_ok: boolean;
  vector_store_ok: boolean;
  document_count: number;
}

export interface FlaggedItem {
  claim_text: string;
  flag_type: "unsupported" | "contradicted" | "unverifiable";
  explanation: string;
  conflicting_source: string | null;
}

export const TIER_LABELS: Record<SourceTier, string> = {
  tier_1_manufacturer: "Manufacturer",
  tier_2_academic: "Academic",
  tier_3_trusted_forum: "Trusted Forum",
  tier_4_unverified: "Unverified",
};

export const TIER_COLORS: Record<SourceTier, string> = {
  tier_1_manufacturer: "text-tier-1",
  tier_2_academic: "text-tier-2",
  tier_3_trusted_forum: "text-tier-3",
  tier_4_unverified: "text-tier-4",
};
