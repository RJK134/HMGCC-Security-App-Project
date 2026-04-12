/** Table/list view of documents as alternative to grid. */

import { Code, File, FileSpreadsheet, FileText, Image, Loader2 } from "lucide-react";
import { useNavigate } from "react-router-dom";
import type { DocumentMetadata, DocumentType } from "../../types";
import { TierBadge } from "./SourceTierSelector";

const TYPE_ICON: Record<DocumentType, typeof File> = {
  pdf: FileText, image: Image, code: Code, text: File,
  spreadsheet: FileSpreadsheet, schematic: Image,
};

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

interface Props {
  documents: DocumentMetadata[];
}

export function DocumentList({ documents }: Props) {
  const navigate = useNavigate();

  if (!documents.length) return null; // Grid handles empty state

  return (
    <div className="border border-sra-border rounded-lg overflow-hidden">
      {/* Header */}
      <div className="grid grid-cols-[auto_1fr_80px_60px_100px_100px_60px] gap-2 px-3 py-2 bg-sra-sidebar text-[10px] font-semibold text-sra-muted uppercase">
        <span className="w-5" />
        <span>Filename</span>
        <span>Size</span>
        <span>Pages</span>
        <span>Source Tier</span>
        <span>Imported</span>
        <span>Status</span>
      </div>

      {/* Rows */}
      {documents.map((doc) => {
        const Icon = TYPE_ICON[doc.filetype] ?? File;
        return (
          <button
            key={doc.id}
            onClick={() => navigate(`/library/${doc.id}`)}
            className="grid grid-cols-[auto_1fr_80px_60px_100px_100px_60px] gap-2 items-center px-3 py-2 text-xs hover:bg-gray-50 dark:hover:bg-gray-800/50 w-full text-left border-t border-sra-border"
          >
            <Icon size={14} className="text-sra-muted" />
            <span className="truncate" title={doc.filename}>{doc.filename}</span>
            <span className="text-sra-muted">{formatSize(doc.size_bytes)}</span>
            <span className="text-sra-muted">{doc.page_count ?? "—"}</span>
            <TierBadge tier={doc.source_tier} />
            <span className="text-sra-muted">{new Date(doc.import_timestamp).toLocaleDateString()}</span>
            <span>
              {doc.status === "indexed" && <span className="w-2 h-2 rounded-full bg-green-500 inline-block" />}
              {doc.status === "processing" && <Loader2 size={12} className="animate-spin text-amber-500" />}
              {doc.status === "failed" && <span className="w-2 h-2 rounded-full bg-red-500 inline-block" />}
            </span>
          </button>
        );
      })}
    </div>
  );
}
