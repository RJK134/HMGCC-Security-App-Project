/** Right sidebar showing source documents used in the last response. */

import { ChevronDown, ChevronUp, ExternalLink, X } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import type { Citation } from "../../types";
import { TIER_LABELS } from "../../types";

const TIER_DOT: Record<string, string> = {
  tier_1_manufacturer: "bg-tier-1",
  tier_2_academic: "bg-tier-2",
  tier_3_trusted_forum: "bg-tier-3",
  tier_4_unverified: "bg-tier-4",
};

interface Props {
  citations: Citation[];
  highlightedChunkId?: string | null;
  onClose: () => void;
}

export function SourcePanel({ citations, highlightedChunkId, onClose }: Props) {
  const navigate = useNavigate();

  if (!citations.length) {
    return (
      <div className="w-[350px] border-l border-sra-border bg-sra-sidebar p-4 shrink-0">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold">Sources</h3>
          <button onClick={onClose} className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded min-w-[32px] min-h-[32px] flex items-center justify-center" aria-label="Close sources panel">
            <X size={18} />
          </button>
        </div>
        <p className="text-xs text-sra-muted">No sources for this response.</p>
      </div>
    );
  }

  return (
    <div className="w-[350px] border-l border-sra-border bg-sra-sidebar shrink-0 flex flex-col overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-sra-border">
        <h3 className="text-sm font-semibold">Sources ({citations.length})</h3>
        <button onClick={onClose} className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded">
          <X size={14} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {citations.map((cit, i) => (
          <SourceCard
            key={`${cit.chunk_id}-${i}`}
            citation={cit}
            isHighlighted={cit.chunk_id === highlightedChunkId}
            onViewInLibrary={() => navigate(`/library/${cit.document_id}`)}
          />
        ))}
      </div>
    </div>
  );
}

function SourceCard({
  citation,
  isHighlighted,
  onViewInLibrary,
}: {
  citation: Citation;
  isHighlighted: boolean;
  onViewInLibrary: () => void;
}) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div
      className={`rounded-lg border p-3 text-xs transition-colors ${
        isHighlighted
          ? "border-sra-accent bg-sra-accent/5"
          : "border-sra-border bg-sra-card"
      }`}
      id={`source-${citation.chunk_id}`}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <p className="font-medium truncate">{citation.document_name}</p>
          <div className="flex items-center gap-2 mt-0.5 text-sra-muted">
            {citation.page_number != null && <span>Page {citation.page_number}</span>}
            <span>{(citation.relevance_score * 100).toFixed(0)}% match</span>
          </div>
          {citation.source_tier && (
            <div className="flex items-center gap-1 mt-1 text-[10px] text-sra-muted">
              <span
                className={`inline-block w-2 h-2 rounded-full ${
                  TIER_DOT[citation.source_tier] ?? "bg-gray-400"
                }`}
              />
              <span>{TIER_LABELS[citation.source_tier]}</span>
            </div>
          )}
        </div>
        <button
          onClick={onViewInLibrary}
          className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded shrink-0"
          title="View in Library"
        >
          <ExternalLink size={12} />
        </button>
      </div>

      {/* Excerpt */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-1 mt-2 text-sra-muted hover:text-sra-text w-full text-left"
      >
        {expanded ? <ChevronUp size={10} /> : <ChevronDown size={10} />}
        <span>Excerpt</span>
      </button>

      {expanded && (
        <p className="mt-1 text-sra-muted leading-relaxed whitespace-pre-wrap">
          {citation.excerpt}
        </p>
      )}
    </div>
  );
}
