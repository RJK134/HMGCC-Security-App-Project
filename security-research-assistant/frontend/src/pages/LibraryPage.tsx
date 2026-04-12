/** Library page — placeholder for Sprint 3.3. */

import { FolderOpen } from "lucide-react";

export function LibraryPage() {
  return (
    <div className="h-full flex flex-col items-center justify-center text-center">
      <FolderOpen size={48} className="text-sra-muted mb-4" />
      <h1 className="text-xl font-semibold mb-2">Document Library</h1>
      <p className="text-sra-muted max-w-md">
        Drag-and-drop document import, library grid view, and document
        management will be built in Sprint 3.3.
      </p>
    </div>
  );
}
