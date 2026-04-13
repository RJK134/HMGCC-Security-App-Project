/** Project selector dropdown for the top bar. */

import { ChevronDown, FolderPlus } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useProjects, useCreateProject } from "../../hooks/useProjects";
import { useAppStore } from "../../stores/appStore";

export function ProjectSelector() {
  const { currentProjectId, setCurrentProject } = useAppStore();
  const { data: projects, isLoading } = useProjects();
  const createProject = useCreateProject();
  const [open, setOpen] = useState(false);
  const [newName, setNewName] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  // Close on outside click
  useEffect(() => {
    function handler(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  // Auto-select first project
  useEffect(() => {
    if (!currentProjectId && projects && projects.length > 0) {
      setCurrentProject(projects[0].id);
    }
  }, [projects, currentProjectId, setCurrentProject]);

  const current = projects?.find((p) => p.id === currentProjectId);

  const [createError, setCreateError] = useState("");

  const handleCreate = async () => {
    if (!newName.trim()) return;
    setCreateError("");
    try {
      const project = await createProject.mutateAsync({ name: newName.trim() });
      setCurrentProject(project.id);
      setNewName("");
      setShowCreate(false);
      setOpen(false);
    } catch (err) {
      setCreateError(
        err instanceof Error ? err.message : "Failed to create project. Check backend connection."
      );
    }
  };

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-sra-border hover:bg-gray-100 dark:hover:bg-gray-800 text-sm min-w-[180px]"
      >
        <span className="truncate">{current?.name || "Select Project"}</span>
        <ChevronDown size={14} />
      </button>

      {open && (
        <div className="absolute top-full mt-1 left-0 w-72 bg-sra-card border border-sra-border rounded-lg shadow-lg z-50 max-h-64 overflow-y-auto">
          {isLoading && (
            <div className="px-3 py-2 text-sm text-sra-muted">Loading...</div>
          )}

          {projects?.map((p) => (
            <button
              key={p.id}
              onClick={() => { setCurrentProject(p.id); setOpen(false); }}
              className={`w-full text-left px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-800 text-sm flex justify-between ${
                p.id === currentProjectId ? "bg-sra-accent/10 text-sra-accent" : ""
              }`}
            >
              <span className="truncate">{p.name}</span>
              <span className="text-xs text-sra-muted ml-2">{p.document_count} docs</span>
            </button>
          ))}

          {!showCreate ? (
            <button
              onClick={() => setShowCreate(true)}
              className="w-full text-left px-3 py-2 text-sm text-sra-accent hover:bg-gray-100 dark:hover:bg-gray-800 flex items-center gap-2 border-t border-sra-border"
            >
              <FolderPlus size={14} />
              New Project
            </button>
          ) : (
            <div className="px-3 py-2 border-t border-sra-border">
              <input
                type="text"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleCreate()}
                placeholder="Project name..."
                className="w-full text-sm px-2 py-1 rounded border border-sra-border bg-transparent focus:outline-none focus:ring-1 focus:ring-sra-accent"
                autoFocus
              />
              {createError && (
                <p className="text-[10px] text-red-500 mt-1">{createError}</p>
              )}
              <div className="flex gap-2 mt-1">
                <button onClick={handleCreate} disabled={createProject.isPending} className="text-xs text-sra-accent hover:underline disabled:opacity-50">
                  {createProject.isPending ? "Creating..." : "Create"}
                </button>
                <button onClick={() => { setShowCreate(false); setCreateError(""); }} className="text-xs text-sra-muted hover:underline">
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
