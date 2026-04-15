/** Navigation sidebar with page links and conversation list. */

import {
  FileText,
  FolderOpen,
  MessageSquare,
  Network,
  Pencil,
  Plus,
  Settings,
  Trash2,
} from "lucide-react";
import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAppStore } from "../../stores/appStore";
import { useConversations, useDeleteConversation } from "../../hooks/useConversations";

const NAV_ITEMS = [
  { path: "/chat", icon: MessageSquare, label: "Chat" },
  { path: "/library", icon: FolderOpen, label: "Library" },
  { path: "/architecture", icon: Network, label: "Architecture" },
  { path: "/reports", icon: FileText, label: "Reports" },
  { path: "/settings", icon: Settings, label: "Settings" },
] as const;

export function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { sidebarCollapsed, currentProjectId, setCurrentConversation } = useAppStore();
  const { data: conversations } = useConversations(currentProjectId);

  return (
    <aside
      className={`${
        sidebarCollapsed ? "w-14" : "w-56"
      } border-r border-sra-border bg-sra-sidebar flex flex-col shrink-0 transition-all duration-200`}
    >
      {/* Navigation */}
      <nav className="flex flex-col gap-0.5 p-2">
        {NAV_ITEMS.map(({ path, icon: Icon, label }) => {
          const isActive = location.pathname.startsWith(path);
          return (
            <button
              key={path}
              onClick={() => navigate(path)}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                isActive
                  ? "bg-sra-accent/10 text-sra-accent font-medium"
                  : "text-sra-muted hover:bg-gray-100 dark:hover:bg-gray-800"
              }`}
              title={label}
            >
              <Icon size={18} />
              {!sidebarCollapsed && <span>{label}</span>}
            </button>
          );
        })}
      </nav>

      {/* Conversation list */}
      {!sidebarCollapsed && currentProjectId && (
        <div className="flex-1 border-t border-sra-border mt-2 flex flex-col min-h-0">
          <div className="flex items-center justify-between px-3 py-2">
            <span className="text-xs font-medium text-sra-muted uppercase">
              Conversations
            </span>
            <button
              onClick={() => {
                setCurrentConversation(null);
                navigate("/chat");
              }}
              className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
              title="New conversation"
            >
              <Plus size={14} />
            </button>
          </div>
          <ConversationList
            conversations={conversations ?? []}
            currentConversationId={useAppStore.getState().currentConversationId}
            onSelect={(id) => { setCurrentConversation(id); navigate(`/chat/${id}`); }}
          />
        </div>
      )}
    </aside>
  );
}

/** Date-grouped conversation list with rename/delete actions. */
function ConversationList({
  conversations,
  currentConversationId,
  onSelect,
}: {
  conversations: { id: string; title: string; updated_at: string }[];
  currentConversationId: string | null;
  onSelect: (id: string) => void;
}) {
  const deleteConv = useDeleteConversation();
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");

  if (!conversations.length) {
    return <p className="text-xs text-sra-muted px-2 py-1">No conversations yet</p>;
  }

  // Group by date
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yesterday = new Date(today.getTime() - 86400000);
  const weekAgo = new Date(today.getTime() - 7 * 86400000);

  const groups: Record<string, typeof conversations> = {
    Today: [], Yesterday: [], "This Week": [], Older: [],
  };
  for (const c of conversations) {
    const d = new Date(c.updated_at);
    if (d >= today) groups.Today.push(c);
    else if (d >= yesterday) groups.Yesterday.push(c);
    else if (d >= weekAgo) groups["This Week"].push(c);
    else groups.Older.push(c);
  }

  const handleRename = async (id: string) => {
    if (!editTitle.trim()) { setEditingId(null); return; }
    try {
      await fetch(`/api/v1/conversations/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: editTitle.trim() }),
      });
      setEditingId(null);
    } catch { setEditingId(null); }
  };

  return (
    <div className="flex-1 overflow-y-auto px-2 pb-2">
      {Object.entries(groups).map(([label, items]) =>
        items.length > 0 && (
          <div key={label}>
            <p className="text-[9px] text-sra-muted uppercase px-2 pt-2 pb-0.5">{label}</p>
            {items.map((conv) => (
              <div key={conv.id} className="group flex items-center gap-0.5">
                {editingId === conv.id ? (
                  <input
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleRename(conv.id)}
                    onBlur={() => handleRename(conv.id)}
                    className="flex-1 text-xs px-2 py-1 rounded border border-sra-accent bg-transparent focus:outline-none"
                    autoFocus
                  />
                ) : (
                  <button
                    onClick={() => onSelect(conv.id)}
                    className={`flex-1 text-left px-2 py-1.5 rounded text-xs truncate ${
                      conv.id === currentConversationId
                        ? "text-sra-accent bg-sra-accent/10"
                        : "text-sra-muted hover:bg-gray-100 dark:hover:bg-gray-800"
                    }`}
                    title={conv.title}
                  >
                    {conv.title}
                  </button>
                )}
                <button
                  onClick={() => { setEditingId(conv.id); setEditTitle(conv.title); }}
                  className="opacity-0 group-hover:opacity-60 p-0.5"
                  title="Rename"
                >
                  <Pencil size={10} />
                </button>
                <button
                  onClick={() => { if (confirm("Delete this conversation?")) deleteConv.mutate(conv.id); }}
                  className="opacity-0 group-hover:opacity-60 p-0.5 text-red-400"
                  title="Delete"
                >
                  <Trash2 size={10} />
                </button>
              </div>
            ))}
          </div>
        ),
      )}
    </div>
  );
}
