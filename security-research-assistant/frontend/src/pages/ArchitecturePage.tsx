/** Architecture page — placeholder for Sprint 4.1. */

import { Network } from "lucide-react";

export function ArchitecturePage() {
  return (
    <div className="h-full flex flex-col items-center justify-center text-center">
      <Network size={48} className="text-sra-muted mb-4" />
      <h1 className="text-xl font-semibold mb-2">System Architecture</h1>
      <p className="text-sra-muted max-w-md">
        Component extraction, relationship mapping, and interactive
        architecture diagrams will be built in Sprint 4.1.
      </p>
    </div>
  );
}
