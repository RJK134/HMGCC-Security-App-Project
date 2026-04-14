/** Reports page — generate, view, and export structured research reports. */

import { Download, FileText, Loader2, Plus, Trash2 } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useAppStore } from "../stores/appStore";

const API = "/api/v1";

const REPORT_TYPES = [
  { value: "product_overview", label: "Product Overview", desc: "Complete product description with component inventory and architecture" },
  { value: "component_analysis", label: "Component Analysis", desc: "Detailed analysis of individual hardware and software components" },
  { value: "system_architecture", label: "System Architecture", desc: "Architecture overview with communication map and security surface" },
  { value: "investigation_summary", label: "Investigation Summary", desc: "Synthesised findings from conversations, pinned facts, and queries" },
];

interface ReportListItem {
  id: string;
  report_type: string;
  title: string;
  generated_at: string;
  metadata: Record<string, unknown>;
}

interface ReportFull {
  id: string;
  title: string;
  report_type: string;
  generated_at: string;
  sections: { heading: string; content: string; confidence_note?: string }[];
  metadata: Record<string, unknown>;
}

export function ReportsPage() {
  const { currentProjectId } = useAppStore();
  const [reports, setReports] = useState<ReportListItem[]>([]);
  const [selectedReport, setSelectedReport] = useState<ReportFull | null>(null);
  const [selectedType, setSelectedType] = useState("product_overview");
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchReports = useCallback(async () => {
    if (!currentProjectId) return;
    try {
      const res = await fetch(`${API}/reports?project_id=${currentProjectId}`);
      const data = await res.json();
      setReports(data.reports ?? []);
    } catch { /* ignore */ }
  }, [currentProjectId]);

  useEffect(() => { fetchReports(); }, [fetchReports]);

  const generateReport = async () => {
    if (!currentProjectId) return;
    setGenerating(true);
    setError(null);
    try {
      const res = await fetch(`${API}/reports/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project_id: currentProjectId, report_type: selectedType }),
      });
      if (!res.ok) throw new Error(`Generation failed: ${res.status}`);
      const data = await res.json();
      setSelectedReport(data.report);
      fetchReports();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed");
    } finally {
      setGenerating(false);
    }
  };

  const viewReport = async (id: string) => {
    try {
      const res = await fetch(`${API}/reports/${id}`);
      const data = await res.json();
      setSelectedReport(data.report);
    } catch { /* ignore */ }
  };

  const exportReport = (id: string, format: string) => {
    window.open(`${API}/reports/${id}/export?format=${format}`, "_blank");
  };

  const deleteReport = async (id: string) => {
    await fetch(`${API}/reports/${id}`, { method: "DELETE" });
    if (selectedReport?.id === id) setSelectedReport(null);
    fetchReports();
  };

  if (!currentProjectId) {
    return <div className="h-full flex items-center justify-center text-sra-muted">Select a project first.</div>;
  }

  return (
    <div className="flex gap-4 h-full">
      {/* Left panel — generator + list */}
      <div className="w-80 shrink-0 space-y-4 overflow-y-auto">
        {/* Generator */}
        <div className="bg-sra-card border border-sra-border rounded-lg p-4 space-y-3">
          <h2 className="text-sm font-semibold flex items-center gap-2"><Plus size={14} /> Generate Report</h2>
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="w-full text-xs px-2 py-1.5 rounded border border-sra-border bg-transparent focus:ring-1 focus:ring-sra-accent focus:outline-none"
          >
            {REPORT_TYPES.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
          <p className="text-[10px] text-sra-muted">
            {REPORT_TYPES.find((t) => t.value === selectedType)?.desc}
          </p>
          <button
            onClick={generateReport}
            disabled={generating}
            className="w-full flex items-center justify-center gap-1.5 px-3 py-2 text-xs bg-sra-accent text-white rounded-lg hover:opacity-90 disabled:opacity-50"
          >
            {generating ? <Loader2 size={14} className="animate-spin" /> : <FileText size={14} />}
            {generating ? "Generating..." : "Generate Report"}
          </button>
          {error && <p className="text-[10px] text-red-500">{error}</p>}
        </div>

        {/* Report list */}
        <div className="bg-sra-card border border-sra-border rounded-lg">
          <div className="px-3 py-2 border-b border-sra-border">
            <h3 className="text-xs font-semibold">Previous Reports ({reports.length})</h3>
          </div>
          <div className="divide-y divide-sra-border max-h-96 overflow-y-auto">
            {reports.map((r) => (
              <div key={r.id} className="px-3 py-2 hover:bg-gray-50 dark:hover:bg-gray-800/50">
                <button onClick={() => viewReport(r.id)} className="text-left w-full">
                  <p className="text-xs font-medium truncate">{r.title}</p>
                  <p className="text-[10px] text-sra-muted">{new Date(r.generated_at).toLocaleDateString()}</p>
                </button>
                <div className="flex gap-1 mt-1">
                  {(["markdown", "pdf", "json", "html"] as const).map((fmt) => (
                    <button key={fmt} onClick={() => exportReport(r.id, fmt)}
                      className="text-[9px] px-1.5 py-0.5 rounded border border-sra-border hover:bg-gray-100 dark:hover:bg-gray-700 uppercase">
                      {fmt}
                    </button>
                  ))}
                  <button onClick={() => deleteReport(r.id)}
                    className="text-[9px] px-1 text-red-500 hover:text-red-700 ml-auto">
                    <Trash2 size={10} />
                  </button>
                </div>
              </div>
            ))}
            {reports.length === 0 && (
              <p className="px-3 py-4 text-xs text-sra-muted text-center">No reports generated yet.</p>
            )}
          </div>
        </div>
      </div>

      {/* Right panel — report viewer */}
      <div className="flex-1 overflow-y-auto">
        {selectedReport ? (
          <div className="max-w-3xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
              <h1 className="text-xl font-semibold">{selectedReport.title}</h1>
              <div className="flex gap-1">
                {(["markdown", "pdf", "json", "html"] as const).map((fmt) => (
                  <button key={fmt} onClick={() => exportReport(selectedReport.id, fmt)}
                    className="flex items-center gap-1 text-[10px] px-2 py-1 rounded border border-sra-border hover:bg-gray-100 dark:hover:bg-gray-700 uppercase">
                    <Download size={10} /> {fmt}
                  </button>
                ))}
              </div>
            </div>

            {/* TOC */}
            <div className="bg-sra-card border border-sra-border rounded-lg p-3 mb-4">
              <h3 className="text-xs font-semibold mb-1">Contents</h3>
              <ol className="text-xs text-sra-muted space-y-0.5 list-decimal list-inside">
                {selectedReport.sections.map((s, i) => (
                  <li key={i}>
                    <a href={`#section-${i}`} className="hover:text-sra-accent">{s.heading}</a>
                  </li>
                ))}
              </ol>
            </div>

            {/* Sections */}
            {selectedReport.sections.map((section, i) => (
              <div key={i} id={`section-${i}`} className="mb-6">
                <h2 className="text-lg font-semibold border-b border-sra-border pb-1 mb-2">{section.heading}</h2>
                <div className="prose prose-sm dark:prose-invert max-w-none">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{section.content}</ReactMarkdown>
                </div>
                {section.confidence_note && (
                  <div className="mt-2 bg-amber-50 dark:bg-amber-900/20 border-l-3 border-amber-400 px-3 py-1.5 text-xs text-amber-700 dark:text-amber-300">
                    {section.confidence_note}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-center">
            <FileText size={40} className="text-sra-muted mb-3" />
            <p className="text-sm font-medium">Select or generate a report</p>
            <p className="text-xs text-sra-muted mt-1">
              Reports compile your research findings into structured, exportable documents.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
