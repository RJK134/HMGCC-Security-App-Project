/** Navigation sidebar with page links and conversation list. */

import {
  FileText,
  FolderOpen,
  MessageSquare,
  Network,
  Plus,
  Settings,
} from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAppStore } from "../../stores/appStore";
import { useConversations } from "../../hooks/useConversations";

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
          <div className="flex-1 overflow-y-auto px-2 pb-2">
            {conversations?.map((conv) => (
              <button
                key={conv.id}
                onClick={() => {
                  setCurrentConversation(conv.id);
                  navigate(`/chat/${conv.id}`);
                }}
                className="w-full text-left px-2 py-1.5 rounded text-xs text-sra-muted hover:bg-gray-100 dark:hover:bg-gray-800 truncate"
                title={conv.title}
              >
                {conv.title}
              </button>
            ))}
            {conversations?.length === 0 && (
              <p className="text-xs text-sra-muted px-2 py-1">No conversations yet</p>
            )}
          </div>
        </div>
      )}
    </aside>
  );
}
