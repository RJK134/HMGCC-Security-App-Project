/** First-run setup wizard — guides new users through initial configuration. */

import { CheckCircle, ChevronRight, Loader2, Shield, XCircle } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { useCreateProject } from "../../hooks/useProjects";
import { useHealth } from "../../hooks/useHealth";
import { useAppStore } from "../../stores/appStore";

interface Props {
  onComplete: () => void;
}

type Step = "welcome" | "system_check" | "model_select" | "create_project" | "done";

export function FirstRunWizard({ onComplete }: Props) {
  const [step, setStep] = useState<Step>("welcome");
  const [projectName, setProjectName] = useState("");
  const { data: health, refetch: recheckHealth } = useHealth();
  const createProject = useCreateProject();
  const { setCurrentProject } = useAppStore();

  const handleCreateProject = async () => {
    if (!projectName.trim()) return;
    const project = await createProject.mutateAsync({ name: projectName.trim() });
    setCurrentProject(project.id);
    setStep("done");
  };

  return (
    <div className="h-screen bg-sra-bg flex items-center justify-center">
      <div className="w-full max-w-lg bg-sra-card border border-sra-border rounded-2xl shadow-2xl p-8">
        {step === "welcome" && (
          <div className="text-center space-y-4">
            <Shield size={48} className="mx-auto text-sra-accent" />
            <h1 className="text-2xl font-bold">Security Research Assistant</h1>
            <p className="text-sm text-sra-muted leading-relaxed">
              Welcome to the Smart Personal Assistant for Security Researchers.
              This tool helps you characterise complex industrial systems by indexing,
              searching, and querying technical documentation using local AI.
            </p>
            <p className="text-xs text-sra-muted">
              Everything runs on your machine — no internet connection required.
            </p>
            <button
              onClick={() => setStep("system_check")}
              className="mt-4 flex items-center gap-2 mx-auto px-6 py-2 bg-sra-accent text-white rounded-lg hover:opacity-90"
            >
              Get Started <ChevronRight size={16} />
            </button>
          </div>
        )}

        {step === "system_check" && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold">System Check</h2>
            <div className="space-y-2">
              <CheckItem label="Backend Service" ok={health?.database_ok ?? false} />
              <CheckItem label="Ollama LLM Server" ok={health?.ollama_connected ?? false} />
              <CheckItem label="Database" ok={health?.database_ok ?? false} />
              <CheckItem label="Vector Store" ok={health?.vector_store_ok ?? false} />
              <CheckItem
                label={`LLM Models (${health?.available_models?.length ?? 0} available)`}
                ok={(health?.available_models?.length ?? 0) > 0}
              />
            </div>
            {!health?.ollama_connected && (
              <p className="text-xs text-amber-500">
                Ollama not detected. Start it with: <code className="bg-gray-100 dark:bg-gray-800 px-1 rounded">ollama serve</code>
              </p>
            )}
            <div className="flex gap-2 mt-4">
              <button onClick={() => recheckHealth()} className="px-4 py-2 text-sm border border-sra-border rounded-lg">
                Re-check
              </button>
              <button
                onClick={() => setStep("create_project")}
                className="px-4 py-2 text-sm bg-sra-accent text-white rounded-lg flex items-center gap-1"
              >
                Continue <ChevronRight size={14} />
              </button>
            </div>
          </div>
        )}

        {step === "create_project" && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold">Create Your First Project</h2>
            <p className="text-sm text-sra-muted">
              Each investigation has its own project with separate documents and conversations.
            </p>
            <input
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleCreateProject()}
              placeholder="e.g., ICS Product Assessment"
              className="w-full px-4 py-2 rounded-lg border border-sra-border bg-transparent text-sm focus:ring-2 focus:ring-sra-accent focus:outline-none"
              autoFocus
            />
            <button
              onClick={handleCreateProject}
              disabled={!projectName.trim()}
              className="w-full py-2 bg-sra-accent text-white rounded-lg text-sm disabled:opacity-40"
            >
              Create Project
            </button>
          </div>
        )}

        {step === "done" && (
          <div className="text-center space-y-4">
            <CheckCircle size={48} className="mx-auto text-green-500" />
            <h2 className="text-lg font-semibold">You're All Set!</h2>
            <p className="text-sm text-sra-muted">
              Start by importing documents into your Library, then ask questions in the Chat.
            </p>
            <button
              onClick={onComplete}
              className="px-6 py-2 bg-sra-accent text-white rounded-lg hover:opacity-90"
            >
              Start Using SRA
            </button>
          </div>
        )}

        {/* Step indicator */}
        <div className="flex justify-center gap-2 mt-6">
          {(["welcome", "system_check", "create_project", "done"] as Step[]).map((s) => (
            <div key={s} className={`w-2 h-2 rounded-full ${s === step ? "bg-sra-accent" : "bg-gray-300"}`} />
          ))}
        </div>
      </div>
    </div>
  );
}

function CheckItem({ label, ok }: { label: string; ok: boolean }) {
  return (
    <div className="flex items-center gap-2 text-sm">
      {ok ? (
        <CheckCircle size={16} className="text-green-500" />
      ) : (
        <XCircle size={16} className="text-amber-500" />
      )}
      <span>{label}</span>
    </div>
  );
}
