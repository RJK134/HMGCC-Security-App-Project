/** Document card for the library grid view. */

import {
  Code,
  File,
  FileSpreadsheet,
  FileText,
  Image,
  Loader2,
} from "lucide-react";
import type { DocumentMetadata, DocumentType } from "../../types";
import { TierBadge } from "./SourceTierSelector";

const TYPE_ICON: Record<DocumentType, typeof File> = {
  pdf: FileText,
  image: Image,
  code: Code,
  text: File,
  spreadsheet: FileSpreadsheet,
  schematic: Image,
};

const TYPE_BG: Record<DocumentType, string> = {
  pdf: "bg-red-100 dark:bg-red-900/30",
  image: "bg-purple-100 dark:bg-purple-900/30",
  code: "bg-emerald-100 dark:bg-emerald-900/30",
  text: "bg-blue-100 dark:bg-blue-900/30",
  spreadsheet: "bg-green-100 dark:bg-green-900/30",
  schematic: "bg-orange-100 dark:bg-orange-900/30",
};

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

interface Props {
  document: DocumentMetadata;
  onClick: () => void;
}

export function DocumentCard({ document: doc, onClick }: Props) {
  const Icon = TYPE_ICON[doc.filetype] ?? File;

  return (
    <button
      onClick={onClick}
      className="w-full text-left bg-sra-card border border-sra-border rounded-lg p-3 hover:border-sra-accent/50 hover:shadow-sm transition-all group"
    >
      {/* Type icon */}
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center mb-2 ${TYPE_BG[doc.filetype] ?? "bg-gray-100"}`}>
        <Icon size={20} className="text-sra-muted" />
      </div>

      {/* Filename */}
      <p className="text-sm font-medium truncate" title={doc.filename}>
        {doc.filename}
      </p>

      {/* Metadata */}
      <div className="flex items-center gap-2 mt-1 text-[10px] text-sra-muted">
        <span>{formatSize(doc.size_bytes)}</span>
        {doc.page_count && <span>{doc.page_count} pg</span>}
        <span>{new Date(doc.import_timestamp).toLocaleDateString()}</span>
      </div>

      {/* Tier + status */}
      <div className="flex items-center justify-between mt-2">
        <TierBadge tier={doc.source_tier} />
        {doc.status === "indexed" && (
          <span className="w-2 h-2 rounded-full bg-green-500" title="Indexed" />
        )}
        {doc.status === "processing" && (
          <Loader2 size={12} className="animate-spin text-amber-500" />
        )}
        {doc.status === "failed" && (
          <span className="w-2 h-2 rounded-full bg-red-500" title="Failed" />
        )}
      </div>
    </button>
  );
}
