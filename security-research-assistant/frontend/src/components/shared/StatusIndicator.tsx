/** Health status dot with tooltip and connection warning banner. */

import { AlertTriangle } from "lucide-react";
import { useHealth } from "../../hooks/useHealth";

export function StatusIndicator() {
  const { data, isError, isLoading } = useHealth();

  let color = "bg-gray-400";
  let label = "Checking...";

  if (isLoading) {
    color = "bg-gray-400 animate-pulse";
    label = "Checking backend connection...";
  } else if (isError || !data) {
    color = "bg-red-500";
    label = "Backend unreachable — start the backend server";
  } else if (data.status === "ok") {
    color = "bg-green-500";
    label = `Connected (${data.document_count} docs across all projects)`;
  } else if (data.status === "degraded") {
    color = "bg-amber-500";
    label = "Ollama disconnected — start Ollama to enable AI features";
  } else {
    color = "bg-red-500";
    label = "System error — check backend logs";
  }

  return (
    <div className="flex items-center gap-2 group relative" title={label}>
      <span className={`w-2.5 h-2.5 rounded-full ${color}`} />
      <span className="text-xs text-sra-muted hidden sm:inline">{label}</span>
    </div>
  );
}

/** Full-width warning banner for disconnected state — use at top of Layout. */
export function ConnectionBanner() {
  const { data, isError } = useHealth();

  if (!isError && data?.status === "ok") return null;

  const isBackendDown = isError || !data;
  const isOllamaDown = data?.status === "degraded";

  if (!isBackendDown && !isOllamaDown) return null;

  return (
    <div className={`px-4 py-2 text-xs flex items-center gap-2 ${
      isBackendDown
        ? "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300"
        : "bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300"
    }`}>
      <AlertTriangle size={14} />
      {isBackendDown ? (
        <span>Backend not connected. Start the backend server to use the application.</span>
      ) : (
        <span>AI model not connected. Start Ollama to enable queries and report generation.</span>
      )}
    </div>
  );
}
