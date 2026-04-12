/** Responsive grid of document cards. */

import { FolderOpen } from "lucide-react";
import { useNavigate } from "react-router-dom";
import type { DocumentMetadata } from "../../types";
import { DocumentCard } from "./DocumentCard";

interface Props {
  documents: DocumentMetadata[];
}

export function DocumentGrid({ documents }: Props) {
  const navigate = useNavigate();

  if (!documents.length) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <FolderOpen size={40} className="text-sra-muted mb-3" />
        <p className="text-sm font-medium">No documents imported yet</p>
        <p className="text-xs text-sra-muted mt-1">
          Drag files onto the drop zone above to get started.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
      {documents.map((doc) => (
        <DocumentCard
          key={doc.id}
          document={doc}
          onClick={() => navigate(`/library/${doc.id}`)}
        />
      ))}
    </div>
  );
}
