/** Document detail page — metadata, preview, chunks, tier editor. */

import { ArrowLeft, ChevronDown, ChevronUp, Trash2 } from "lucide-react";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useDeleteDocument, useDocument, useUpdateDocumentTier } from "../hooks/useDocuments";
import { SourceTierSelector, TierBadge } from "../components/library/SourceTierSelector";
import type { SourceTier } from "../types";

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function DocumentDetailPage() {
  const { documentId } = useParams<{ documentId: string }>();
  const navigate = useNavigate();
  const { data, isLoading } = useDocument(documentId ?? null);
  const updateTier = useUpdateDocumentTier();
  const deleteDoc = useDeleteDocument();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [expandedChunk, setExpandedChunk] = useState<number | null>(null);

  if (isLoading) {
    return <div className="p-8 text-sra-muted">Loading document...</div>;
  }

  if (!data?.document) {
    return (
      <div className="p-8 text-center">
        <p className="text-sra-muted">Document not found.</p>
        <button onClick={() => navigate("/library")} className="text-sra-accent text-sm mt-2 hover:underline">
          Back to Library
        </button>
      </div>
    );
  }

  const doc = data.document;
  const chunks = (data.sample_chunks ?? []) as {
    chunk_index: number;
    page_number: number | null;
    section_heading: string | null;
    token_count: number;
    preview: string;
  }[];

  const handleTierChange = (tier: SourceTier) => {
    if (!documentId) return;
    updateTier.mutate({ id: documentId, tier });
  };

  const handleDelete = async () => {
    if (!documentId) return;
    await deleteDoc.mutateAsync(documentId);
    navigate("/library");
  };

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <button
          onClick={() => navigate("/library")}
          className="p-1.5 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
        >
          <ArrowLeft size={18} />
        </button>
        <h1 className="text-lg font-semibold truncate flex-1">{doc.filename}</h1>
        <TierBadge tier={doc.source_tier} size="md" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
        {/* Left: Document info (3 cols) */}
        <div className="lg:col-span-3 space-y-4">
          {/* Metadata card */}
          <div className="bg-sra-card border border-sra-border rounded-lg p-4 space-y-3">
            <h2 className="text-sm font-semibold">Document Information</h2>
            <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-xs">
              <dt className="text-sra-muted">File type</dt>
              <dd className="capitalize">{doc.filetype}</dd>
              <dt className="text-sra-muted">Size</dt>
              <dd>{formatSize(doc.size_bytes)}</dd>
              <dt className="text-sra-muted">Status</dt>
              <dd className="capitalize">{doc.status}</dd>
              <dt className="text-sra-muted">Imported</dt>
              <dd>{new Date(doc.import_timestamp).toLocaleString()}</dd>
              {doc.page_count && (
                <>
                  <dt className="text-sra-muted">Pages</dt>
                  <dd>{doc.page_count}</dd>
                </>
              )}
            </dl>
          </div>

          {/* Source tier editor */}
          <div className="bg-sra-card border border-sra-border rounded-lg p-4">
            <h2 className="text-sm font-semibold mb-2">Source Quality Tier</h2>
            <SourceTierSelector value={doc.source_tier} onChange={handleTierChange} />
          </div>

          {/* Actions */}
          <div className="flex gap-2">
            <button
              onClick={() => navigate(`/chat`)}
              className="px-3 py-1.5 text-xs bg-sra-accent text-white rounded-lg hover:opacity-90"
            >
              Ask about this document
            </button>
            <button
              onClick={() => setShowDeleteConfirm(true)}
              className="px-3 py-1.5 text-xs border border-red-300 text-red-600 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 flex items-center gap-1"
            >
              <Trash2 size={12} /> Delete
            </button>
          </div>

          {/* Delete confirmation */}
          {showDeleteConfirm && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-300 dark:border-red-700 rounded-lg p-3">
              <p className="text-xs font-medium text-red-700 dark:text-red-300">
                This will permanently remove the document and all its indexed data.
              </p>
              <div className="flex gap-2 mt-2">
                <button onClick={handleDelete} className="px-3 py-1 text-xs bg-red-500 text-white rounded hover:bg-red-600">
                  Confirm Delete
                </button>
                <button onClick={() => setShowDeleteConfirm(false)} className="px-3 py-1 text-xs border border-sra-border rounded">
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Right: Chunk browser (2 cols) */}
        <div className="lg:col-span-2">
          <div className="bg-sra-card border border-sra-border rounded-lg">
            <div className="px-4 py-3 border-b border-sra-border">
              <h2 className="text-sm font-semibold">
                Chunks ({data.chunk_count})
              </h2>
            </div>
            <div className="max-h-[500px] overflow-y-auto divide-y divide-sra-border">
              {chunks.map((chunk) => (
                <div key={chunk.chunk_index} className="px-3 py-2">
                  <button
                    onClick={() =>
                      setExpandedChunk(
                        expandedChunk === chunk.chunk_index ? null : chunk.chunk_index,
                      )
                    }
                    className="flex items-center gap-2 w-full text-left text-xs"
                  >
                    <span className="font-mono text-sra-muted w-6">#{chunk.chunk_index}</span>
                    <span className="flex-1 truncate">{chunk.preview}</span>
                    <span className="text-[10px] text-sra-muted shrink-0">
                      {chunk.token_count} tok
                    </span>
                    {expandedChunk === chunk.chunk_index ? (
                      <ChevronUp size={12} />
                    ) : (
                      <ChevronDown size={12} />
                    )}
                  </button>
                  {expandedChunk === chunk.chunk_index && (
                    <div className="mt-2 text-xs text-sra-muted whitespace-pre-wrap bg-gray-50 dark:bg-gray-800/50 rounded p-2">
                      {chunk.preview}
                      {chunk.page_number && (
                        <p className="mt-1 text-[10px]">Page {chunk.page_number}</p>
                      )}
                      {chunk.section_heading && (
                        <p className="text-[10px]">Section: {chunk.section_heading}</p>
                      )}
                    </div>
                  )}
                </div>
              ))}
              {chunks.length === 0 && (
                <p className="px-3 py-4 text-xs text-sra-muted text-center">
                  No chunks available.
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
