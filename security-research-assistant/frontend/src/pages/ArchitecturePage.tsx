/** Architecture page — component extraction, graph visualisation, summary. */

import { Download, Loader2, Network, RefreshCw } from "lucide-react";
import { useCallback, useState } from "react";
import { ComponentMap } from "../components/architecture/ComponentMap";
import { useAppStore } from "../stores/appStore";

interface ArchData {
  graph: { nodes: GraphNode[]; edges: GraphEdge[]; summary: string; incomplete_areas: string[] };
  extraction: { components: Comp[]; interfaces: Iface[]; protocols: Proto[]; software: Sw[] };
  summary: string;
  warnings: string[];
}

interface GraphNode { id: string; label: string; node_type: string; description: string; group: string }
interface GraphEdge { source: string; target: string; label: string }
interface Comp { name: string; component_type: string; description: string }
interface Iface { name: string; connects_from: string; connects_to: string }
interface Proto { name: string; layer: string; description: string }
interface Sw { name: string; software_type: string; version: string }

export function ArchitecturePage() {
  const { currentProjectId } = useAppStore();
  const [data, setData] = useState<ArchData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchArchitecture = useCallback(async () => {
    if (!currentProjectId) return;
    setLoading(true);
    setError(null);
    try {
      // Use the GET endpoint which triggers extraction + returns results
      const res = await fetch(`http://localhost:8000/api/v1/architecture/${currentProjectId}`, {
        signal: AbortSignal.timeout(300000), // 5 min timeout for LLM extraction
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        const stage = body.stage ? ` (during ${body.stage})` : "";
        throw new Error(body.message || `Extraction failed (${res.status})${stage}. Ensure Ollama is running and not busy with another request.`);
      }
      const json = await res.json();
      if (!json.graph?.nodes?.length && !json.extraction?.components?.length) {
        setError("Extraction completed but found no components. Try importing more technical documents (datasheets, schematics).");
      } else {
        setData(json);
      }
    } catch (e) {
      if (e instanceof DOMException && e.name === "TimeoutError") {
        setError("Architecture extraction timed out. This can take several minutes with large document sets.");
      } else {
        setError(e instanceof Error ? e.message : "Failed to extract architecture. Check backend logs.");
      }
    } finally {
      setLoading(false);
    }
  }, [currentProjectId]);

  const exportJson = useCallback(() => {
    if (!data) return;
    const blob = new Blob([JSON.stringify(data.graph, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "architecture.json";
    a.click();
    URL.revokeObjectURL(url);
  }, [data]);

  if (!currentProjectId) {
    return (
      <div className="h-full flex items-center justify-center text-sra-muted">
        Select a project to view its system architecture.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Network size={24} />
          <h1 className="text-xl font-semibold">System Architecture</h1>
        </div>
        <div className="flex gap-2">
          <button
            onClick={fetchArchitecture}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs bg-sra-accent text-white rounded-lg hover:opacity-90 disabled:opacity-50"
          >
            {loading ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
            {data ? "Re-extract" : "Extract Architecture"}
          </button>
          {data && (
            <button
              onClick={exportJson}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs border border-sra-border rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
            >
              <Download size={14} /> Export JSON
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-300 dark:border-red-700 rounded-lg p-3 text-xs text-red-700 dark:text-red-300">
          {error}
        </div>
      )}

      {loading && (
        <div className="bg-sra-card border border-sra-border rounded-lg p-8 text-center">
          <Loader2 size={32} className="animate-spin mx-auto text-sra-accent mb-3" />
          <p className="text-sm font-medium mb-1">Extracting architecture...</p>
          <p className="text-xs text-sra-muted">
            The LLM is analysing your documents to identify components, interfaces,
            protocols, and software. This may take several minutes.
          </p>
          <p className="text-xs text-sra-muted mt-2">Do not navigate away from this page.</p>
        </div>
      )}

      {!data && !loading && (
        <div className="bg-sra-card border border-sra-border rounded-lg p-8 text-center">
          <Network size={40} className="mx-auto text-sra-muted mb-3" />
          <p className="text-sm font-medium mb-1">No architecture data yet</p>
          <p className="text-xs text-sra-muted">
            Click "Extract Architecture" to analyse your imported documents and build
            a component map showing hardware, interfaces, protocols, and software.
          </p>
        </div>
      )}

      {data && (
        <>
          {/* Summary */}
          <div className="bg-sra-card border border-sra-border rounded-lg p-4">
            <h2 className="text-sm font-semibold mb-2">Architecture Summary</h2>
            <p className="text-xs text-sra-muted leading-relaxed">{data.summary}</p>
          </div>

          {/* Interactive diagram */}
          <ComponentMap
            nodes={data.graph.nodes}
            edges={data.graph.edges}
          />

          {/* Stats and details */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <StatCard label="Components" count={data.extraction.components.length} items={data.extraction.components.map(c => `${c.name} (${c.component_type})`)} />
            <StatCard label="Interfaces" count={data.extraction.interfaces.length} items={data.extraction.interfaces.map(i => `${i.name}: ${i.connects_from} → ${i.connects_to}`)} />
            <StatCard label="Protocols" count={data.extraction.protocols.length} items={data.extraction.protocols.map(p => p.name)} />
            <StatCard label="Software" count={data.extraction.software.length} items={data.extraction.software.map(s => `${s.name} ${s.version}`)} />
          </div>

          {/* Warnings */}
          {data.warnings.length > 0 && (
            <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-300 dark:border-amber-700 rounded-lg p-3">
              <h3 className="text-xs font-semibold text-amber-700 dark:text-amber-300 mb-1">
                Incomplete Areas
              </h3>
              <ul className="text-xs text-amber-600 dark:text-amber-400 space-y-0.5">
                {data.warnings.map((w, i) => <li key={i}>&bull; {w}</li>)}
              </ul>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function StatCard({ label, count, items }: { label: string; count: number; items: string[] }) {
  const [open, setOpen] = useState(false);
  return (
    <button
      onClick={() => setOpen(!open)}
      className="bg-sra-card border border-sra-border rounded-lg p-3 text-left hover:border-sra-accent/50"
    >
      <p className="text-2xl font-bold">{count}</p>
      <p className="text-xs text-sra-muted">{label}</p>
      {open && items.length > 0 && (
        <ul className="mt-2 text-[10px] text-sra-muted space-y-0.5 max-h-24 overflow-y-auto">
          {items.map((item, i) => <li key={i}>&bull; {item}</li>)}
        </ul>
      )}
    </button>
  );
}
