/** Custom hook for SSE streaming queries to the RAG engine. */

import { useCallback, useRef, useState } from "react";
import { queryPost } from "../api/client";
import type { Citation, ConfidenceResult, QueryRequest } from "../types";

interface StreamState {
  streamedText: string;
  isStreaming: boolean;
  citations: Citation[];
  confidence: ConfidenceResult | null;
  conversationId: string | null;
  error: string | null;
}

export function useStreamingQuery() {
  const [state, setState] = useState<StreamState>({
    streamedText: "",
    isStreaming: false,
    citations: [],
    confidence: null,
    conversationId: null,
    error: null,
  });
  const abortRef = useRef<AbortController | null>(null);

  const sendQuery = useCallback(async (request: QueryRequest) => {
    // Reset state
    setState({
      streamedText: "",
      isStreaming: true,
      citations: [],
      confidence: null,
      conversationId: null,
      error: null,
    });

    abortRef.current = new AbortController();

    try {
      const response = await fetch("http://localhost:8000/api/v1/query?stream=true", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
        signal: abortRef.current.signal,
      });

      if (!response.ok || !response.body) {
        throw new Error(`Query failed: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let accumulated = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("event: ")) continue;
          if (line.startsWith("data: ")) {
            const data = line.slice(6);
            try {
              const parsed = JSON.parse(data);
              if (parsed.token) {
                accumulated += parsed.token;
                setState((prev) => ({ ...prev, streamedText: accumulated }));
              } else if (parsed.citations) {
                setState((prev) => ({
                  ...prev,
                  citations: parsed.citations || [],
                  confidence: parsed.confidence || null,
                  conversationId: parsed.conversation_id || null,
                  isStreaming: false,
                }));
              } else if (parsed.error) {
                setState((prev) => ({ ...prev, error: parsed.error, isStreaming: false }));
              }
            } catch {
              // Skip unparseable lines
            }
          }
        }
      }

      setState((prev) => ({ ...prev, isStreaming: false }));
    } catch (err) {
      if (err instanceof DOMException && err.name === "AbortError") return;
      setState((prev) => ({
        ...prev,
        error: err instanceof Error ? err.message : "Query failed",
        isStreaming: false,
      }));
    }
  }, []);

  const cancel = useCallback(() => {
    abortRef.current?.abort();
    setState((prev) => ({ ...prev, isStreaming: false }));
  }, []);

  return { ...state, sendQuery, cancel };
}
