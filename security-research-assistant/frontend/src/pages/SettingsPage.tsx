/** Settings page — model selection, RAG parameters, theme. */

import { RefreshCw, Save, Settings } from "lucide-react";
import { useHealth } from "../hooks/useHealth";
import { useAppStore } from "../stores/appStore";

export function SettingsPage() {
  const { theme, setTheme } = useAppStore();
  const { data: health } = useHealth();

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex items-center gap-3 mb-6">
        <Settings size={24} />
        <h1 className="text-xl font-semibold">Settings</h1>
      </div>

      {/* Model Selection */}
      <section className="bg-sra-card border border-sra-border rounded-lg p-4">
        <h2 className="text-sm font-semibold mb-3">LLM Model</h2>
        <div className="space-y-3">
          <div>
            <label className="text-xs text-sra-muted block mb-1">Available Models</label>
            <select className="w-full rounded border border-sra-border bg-transparent px-2 py-1.5 text-sm focus:ring-1 focus:ring-sra-accent focus:outline-none">
              {health?.available_models?.map((m) => (
                <option key={m} value={m}>{m}</option>
              )) ?? <option>No models available</option>}
            </select>
          </div>
          <p className="text-xs text-sra-muted">
            Ollama status: {health?.ollama_connected ? "Connected" : "Disconnected"}
          </p>
        </div>
      </section>

      {/* RAG Settings */}
      <section className="bg-sra-card border border-sra-border rounded-lg p-4">
        <h2 className="text-sm font-semibold mb-3">Retrieval Settings</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-xs text-sra-muted block mb-1">Top-K Results</label>
            <input
              type="number"
              defaultValue={10}
              min={1}
              max={50}
              className="w-full rounded border border-sra-border bg-transparent px-2 py-1.5 text-sm focus:ring-1 focus:ring-sra-accent focus:outline-none"
            />
          </div>
          <div>
            <label className="text-xs text-sra-muted block mb-1">Chunk Size</label>
            <input
              type="number"
              defaultValue={512}
              className="w-full rounded border border-sra-border bg-transparent px-2 py-1.5 text-sm focus:ring-1 focus:ring-sra-accent focus:outline-none"
            />
          </div>
          <div>
            <label className="text-xs text-sra-muted block mb-1">Chunk Overlap</label>
            <input
              type="number"
              defaultValue={50}
              className="w-full rounded border border-sra-border bg-transparent px-2 py-1.5 text-sm focus:ring-1 focus:ring-sra-accent focus:outline-none"
            />
          </div>
          <div>
            <label className="text-xs text-sra-muted block mb-1">Max Context Tokens</label>
            <input
              type="number"
              defaultValue={4096}
              className="w-full rounded border border-sra-border bg-transparent px-2 py-1.5 text-sm focus:ring-1 focus:ring-sra-accent focus:outline-none"
            />
          </div>
        </div>
      </section>

      {/* Appearance */}
      <section className="bg-sra-card border border-sra-border rounded-lg p-4">
        <h2 className="text-sm font-semibold mb-3">Appearance</h2>
        <div className="flex items-center gap-4">
          <span className="text-sm">Theme:</span>
          <button
            onClick={() => setTheme("light")}
            className={`px-3 py-1 rounded text-sm ${
              theme === "light" ? "bg-sra-accent text-white" : "border border-sra-border"
            }`}
          >
            Light
          </button>
          <button
            onClick={() => setTheme("dark")}
            className={`px-3 py-1 rounded text-sm ${
              theme === "dark" ? "bg-sra-accent text-white" : "border border-sra-border"
            }`}
          >
            Dark
          </button>
        </div>
      </section>

      {/* About */}
      <section className="bg-sra-card border border-sra-border rounded-lg p-4">
        <h2 className="text-sm font-semibold mb-3">About</h2>
        <div className="text-xs text-sra-muted space-y-1">
          <p>Security Research Assistant v0.1.0</p>
          <p>HMGCC Co-Creation Challenge (CH-2026-001)</p>
          <p>Fully offline operation — no internet required</p>
          <p>Documents indexed: {health?.document_count ?? "—"}</p>
        </div>
      </section>

      {/* Actions */}
      <div className="flex gap-3">
        <button className="flex items-center gap-2 px-4 py-2 bg-sra-accent text-white rounded-lg text-sm hover:opacity-90">
          <Save size={16} /> Save Settings
        </button>
        <button className="flex items-center gap-2 px-4 py-2 border border-sra-border rounded-lg text-sm hover:bg-gray-100 dark:hover:bg-gray-800">
          <RefreshCw size={16} /> Reset to Defaults
        </button>
      </div>
    </div>
  );
}
