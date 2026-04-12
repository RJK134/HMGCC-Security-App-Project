/** Health status dot with tooltip. */

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
    label = "Backend unreachable";
  } else if (data.status === "ok") {
    color = "bg-green-500";
    label = `All systems OK (${data.document_count} docs)`;
  } else if (data.status === "degraded") {
    color = "bg-amber-500";
    label = "Ollama disconnected — LLM features unavailable";
  } else {
    color = "bg-red-500";
    label = "System error";
  }

  return (
    <div className="flex items-center gap-2 group relative" title={label}>
      <span className={`w-2.5 h-2.5 rounded-full ${color}`} />
      <span className="text-xs text-sra-muted hidden sm:inline">{label}</span>
    </div>
  );
}
