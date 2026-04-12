/** Chat page — placeholder for Sprint 3.2. */

import { MessageSquare } from "lucide-react";
import { useAppStore } from "../stores/appStore";

export function ChatPage() {
  const { currentProjectId } = useAppStore();

  return (
    <div className="h-full flex flex-col items-center justify-center text-center">
      <MessageSquare size={48} className="text-sra-muted mb-4" />
      <h1 className="text-xl font-semibold mb-2">Chat Interface</h1>
      <p className="text-sra-muted max-w-md">
        The conversational query interface will be built in Sprint 3.2.
        Ask natural-language questions about your indexed documents and receive
        cited, confidence-scored answers.
      </p>
      {!currentProjectId && (
        <p className="text-amber-500 mt-4 text-sm">
          Select or create a project to get started.
        </p>
      )}
    </div>
  );
}
