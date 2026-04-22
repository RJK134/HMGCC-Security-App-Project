/** Main chat container — message list, streaming, input. */

import { useQueryClient } from "@tanstack/react-query";
import { ArrowDown, FolderOpen, MessageSquare } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { pinFact } from "../../api/client";
import { useStreamingQuery } from "../../hooks/useStreamingQuery";
import { useAppStore } from "../../stores/appStore";
import type { Citation, ConfidenceResult, Message } from "../../types";
import { InputArea } from "./InputArea";
import { MessageBubble } from "./MessageBubble";

interface Props {
  messages: Message[];
  onCitationClick?: (citation: Citation) => void;
  onStreamCitations?: (citations: Citation[]) => void;
  projectId: string;
  conversationId?: string | null;
}

export function ChatWindow({ messages, onCitationClick, onStreamCitations, projectId, conversationId }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [showScrollBtn, setShowScrollBtn] = useState(false);
  const [localMessages, setLocalMessages] = useState<Message[]>([]);
  const [streamConfidence, setStreamConfidence] = useState<ConfidenceResult | null>(null);
  const [streamFlagged, setStreamFlagged] = useState<string[]>([]);
  const [streamAlternatives, setStreamAlternatives] = useState<string[]>([]);
  const [pinnedIds, setPinnedIds] = useState<Set<string>>(new Set());

  const queryClient = useQueryClient();
  const preStreamCount = useRef(0);
  const prevStreamingRef = useRef(false);

  const {
    streamedText,
    isStreaming,
    citations,
    confidence,
    flaggedClaims,
    alternatives,
    error,
    conversationId: newConvId,
    sendQuery,
    cancel,
    reset,
  } = useStreamingQuery();

  const { setCurrentConversation } = useAppStore();

  // Sync external messages and deduplicate against streaming state
  useEffect(() => {
    setLocalMessages(messages);
    // If DB now has the streamed response, clear streaming state to avoid duplication
    if (!isStreaming && streamedText && messages.length > preStreamCount.current + 1) {
      reset(); // DB message is authoritative — drop streaming message
    }
  }, [messages]);

  // Update conversation ID when backend creates one
  useEffect(() => {
    if (newConvId) setCurrentConversation(newConvId);
  }, [newConvId, setCurrentConversation]);

  // Update confidence when stream completes
  useEffect(() => {
    if (confidence) setStreamConfidence(confidence);
  }, [confidence]);

  useEffect(() => {
    setStreamFlagged(flaggedClaims);
  }, [flaggedClaims]);

  useEffect(() => {
    setStreamAlternatives(alternatives);
  }, [alternatives]);

  // Report streaming citations to parent for source panel
  useEffect(() => {
    if (citations.length > 0) {
      onStreamCitations?.(citations);
    }
  }, [citations, onStreamCitations]);

  // Invalidate conversation cache when streaming ends so DB message (with citations) is fetched
  useEffect(() => {
    if (prevStreamingRef.current && !isStreaming && streamedText) {
      const convId = newConvId || conversationId;
      if (convId) {
        queryClient.invalidateQueries({ queryKey: ["conversation", convId] });
      }
    }
    prevStreamingRef.current = isStreaming;
  }, [isStreaming]);

  // Auto-scroll to bottom on new content
  useEffect(() => {
    if (!showScrollBtn) bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [localMessages, streamedText, showScrollBtn]);

  // Detect scroll position
  const handleScroll = useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 60;
    setShowScrollBtn(!atBottom);
  }, []);

  const handleSend = useCallback(
    (text: string) => {
      // Capture pre-stream message count for deduplication
      preStreamCount.current = localMessages.length;

      // Optimistic user message
      const userMsg: Message = {
        id: crypto.randomUUID(),
        conversation_id: conversationId ?? "",
        role: "user",
        content: text,
        citations: [],
        confidence_score: null,
        created_at: new Date().toISOString(),
      };
      setLocalMessages((prev) => [...prev, userMsg]);
      setStreamConfidence(null);
      setStreamFlagged([]);
      setStreamAlternatives([]);

      sendQuery({
        question: text,
        project_id: projectId,
        conversation_id: conversationId ?? undefined,
      });
    },
    [projectId, conversationId, sendQuery, localMessages.length],
  );

  // Build streaming assistant message
  const streamingMsg: Message | null =
    isStreaming || streamedText
      ? {
          id: "streaming",
          conversation_id: conversationId ?? "",
          role: "assistant",
          content: streamedText || (error ? `Error: ${error}` : ""),
          citations: citations,
          confidence_score: confidence?.score ?? null,
          created_at: new Date().toISOString(),
        }
      : null;

  const allMessages = streamingMsg
    ? [...localMessages, streamingMsg]
    : localMessages;

  const navigate = useNavigate();

  const handlePin = useCallback(
    async (messageId: string, content: string, citationList: Citation[]) => {
      if (!conversationId) return;
      try {
        await pinFact(conversationId, content, citationList);
        setPinnedIds((prev) => new Set(prev).add(messageId));
      } catch (err) {
        console.error("Pin failed:", err);
      }
    },
    [conversationId],
  );

  // Empty state with onboarding guidance
  if (!allMessages.length && !isStreaming) {
    return (
      <div className="flex flex-col h-full">
        <div className="flex-1 flex flex-col items-center justify-center text-center px-4">
          <MessageSquare size={40} className="text-sra-muted mb-3" />
          <h2 className="text-lg font-medium mb-2">Start a conversation</h2>
          <p className="text-sm text-sra-muted max-w-md">
            Ask a question about your imported documents. Responses will cite
            their sources and include confidence scores (0-100).
          </p>
          <div className="mt-4 flex flex-col gap-2 items-center">
            <button
              onClick={() => navigate("/library")}
              className="flex items-center gap-2 text-xs text-sra-accent hover:underline"
            >
              <FolderOpen size={14} />
              Import documents in the Library first
            </button>
            <p className="text-[10px] text-sra-muted">
              Tip: Hover over responses to pin key findings. Click citations to view sources.
            </p>
          </div>
        </div>
        <InputArea onSend={handleSend} onCancel={cancel} isStreaming={isStreaming} />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div
        ref={scrollRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto px-4 py-4 space-y-4"
      >
        {allMessages.map((msg, i) => {
          const isStreamMsg = msg.id === "streaming";
          return (
            <MessageBubble
              key={msg.id}
              message={msg}
              confidence={
                isStreamMsg
                  ? streamConfidence
                  : msg.role === "assistant" && msg.confidence_score != null
                    ? {
                        score: msg.confidence_score,
                        explanation: "",
                        flagged_claims: [],
                        alternative_interpretations: [],
                      }
                    : null
              }
              flaggedClaims={isStreamMsg ? streamFlagged : undefined}
              alternatives={isStreamMsg ? streamAlternatives : undefined}
              onCitationClick={onCitationClick}
              onPin={msg.role === "assistant" ? (content, cits) => handlePin(msg.id, content, cits) : undefined}
              isPinned={pinnedIds.has(msg.id)}
              isStreaming={isStreamMsg && isStreaming}
            />
          );
        })}
        <div ref={bottomRef} />
      </div>

      {/* Scroll to bottom button */}
      {showScrollBtn && (
        <button
          onClick={() => bottomRef.current?.scrollIntoView({ behavior: "smooth" })}
          className="absolute bottom-20 right-8 p-2 rounded-full bg-sra-card border border-sra-border shadow-lg hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          <ArrowDown size={16} />
        </button>
      )}

      {/* Input */}
      <InputArea
        onSend={handleSend}
        onCancel={cancel}
        isStreaming={isStreaming}
      />
    </div>
  );
}
