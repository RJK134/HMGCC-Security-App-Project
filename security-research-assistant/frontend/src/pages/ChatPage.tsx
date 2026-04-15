/** Chat page — main conversational interface with source panel. */

import { BookOpen } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { ChatWindow } from "../components/chat/ChatWindow";
import { SourcePanel } from "../components/chat/SourcePanel";
import { useConversation } from "../hooks/useConversations";
import { useAppStore } from "../stores/appStore";
import type { Citation, Message } from "../types";

export function ChatPage() {
  const { conversationId: urlConvId } = useParams<{ conversationId?: string }>();
  const { currentProjectId, currentConversationId } = useAppStore();
  const activeConvId = urlConvId || currentConversationId;

  const { data: convData } = useConversation(activeConvId);

  const [sourcePanelOpen, setSourcePanelOpen] = useState(false);
  const [sourceCitations, setSourceCitations] = useState<Citation[]>([]);
  const [highlightedChunk, setHighlightedChunk] = useState<string | null>(null);

  // Close source panel on Escape key
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape" && sourcePanelOpen) setSourcePanelOpen(false);
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [sourcePanelOpen]);

  // Auto-populate source panel with citations from the latest assistant message
  const messages: Message[] = convData?.messages
    ? (convData.messages as Message[])
    : [];

  useEffect(() => {
    if (!messages.length) return;
    // Find the last assistant message with citations
    for (let i = messages.length - 1; i >= 0; i--) {
      const msg = messages[i];
      if (msg.role === "assistant" && msg.citations && msg.citations.length > 0) {
        setSourceCitations(msg.citations);
        break;
      }
    }
  }, [messages.length]); // Re-run when message count changes

  // Receive streaming citations from ChatWindow
  const handleStreamCitations = useCallback((citations: Citation[]) => {
    if (citations.length > 0) {
      setSourceCitations(citations);
    }
  }, []);

  const handleCitationClick = useCallback((citation: Citation) => {
    setSourcePanelOpen(true);
    setHighlightedChunk(citation.chunk_id);
    // Collect all citations from the context for the panel
    setSourceCitations((prev) => {
      const exists = prev.some((c) => c.chunk_id === citation.chunk_id);
      return exists ? prev : [...prev, citation];
    });
    // Scroll to the source card
    setTimeout(() => {
      document.getElementById(`source-${citation.chunk_id}`)?.scrollIntoView({ behavior: "smooth" });
    }, 100);
  }, []);

  if (!currentProjectId) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-center">
        <p className="text-sra-muted">Select or create a project to start chatting.</p>
      </div>
    );
  }

  return (
    <div className="h-full flex relative">
      {/* Main chat area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Chat top bar */}
        <div className="flex items-center justify-between px-4 py-2 border-b border-sra-border">
          <h2 className="text-sm font-medium truncate">
            {convData?.conversation
              ? (convData.conversation as { title: string }).title
              : "New Conversation"}
          </h2>
          <button
            onClick={() => setSourcePanelOpen(!sourcePanelOpen)}
            className={`flex items-center gap-1.5 px-2 py-1 rounded text-xs ${
              sourcePanelOpen
                ? "bg-sra-accent/10 text-sra-accent"
                : "text-sra-muted hover:bg-gray-100 dark:hover:bg-gray-800"
            }`}
          >
            <BookOpen size={14} />
            Sources
          </button>
        </div>

        {/* Chat window */}
        <ChatWindow
          messages={messages}
          onCitationClick={handleCitationClick}
          onStreamCitations={handleStreamCitations}
          projectId={currentProjectId}
          conversationId={activeConvId}
        />
      </div>

      {/* Source panel */}
      {sourcePanelOpen && (
        <SourcePanel
          citations={sourceCitations}
          highlightedChunkId={highlightedChunk}
          onClose={() => setSourcePanelOpen(false)}
        />
      )}
    </div>
  );
}
