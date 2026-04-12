/** Reports page — placeholder for Sprint 4.2. */

import { FileText } from "lucide-react";

export function ReportsPage() {
  return (
    <div className="h-full flex flex-col items-center justify-center text-center">
      <FileText size={48} className="text-sra-muted mb-4" />
      <h1 className="text-xl font-semibold mb-2">Report Generation</h1>
      <p className="text-sra-muted max-w-md">
        Product overview reports, architecture reports, and PDF/Markdown
        export will be built in Sprint 4.2.
      </p>
    </div>
  );
}
