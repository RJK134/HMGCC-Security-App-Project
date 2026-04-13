/** Individual chat message — user or assistant with markdown, citations, confidence. */

import { Pin } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Citation, ConfidenceResult, Message } from "../../types";
import { AlternativePanel } from "./AlternativePanel";
import { CitationBadge } from "./CitationBadge";
import { ConfidenceBar } from "./ConfidenceBar";
import { FlaggedClaims } from "./FlaggedClaims";

interface Props {
  message: Message;
  confidence?: ConfidenceResult | null;
  flaggedClaims?: string[];
  alternatives?: string[];
  onCitationClick?: (citation: Citation) => void;
  onPin?: (content: string, citations: Citation[]) => void;
  isStreaming?: boolean;
}

export function MessageBubble({
  message,
  confidence,
  flaggedClaims,
  alternatives,
  onCitationClick,
  onPin,
  isStreaming,
}: Props) {
  const isUser = message.role === "user";
  const ts = new Date(message.created_at).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  if (isUser) {
    return (
      <div className="flex justify-end group">
        <div className="max-w-[75%] bg-sra-accent text-white px-4 py-2 rounded-2xl rounded-br-md">
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          <span className="text-[10px] opacity-0 group-hover:opacity-60 transition-opacity mt-0.5 block text-right">
            {ts}
          </span>
        </div>
      </div>
    );
  }

  // Assistant message
  return (
    <div className="flex justify-start group">
      <div className="max-w-[85%] bg-sra-card border border-sra-border px-4 py-3 rounded-2xl rounded-bl-md">
        {/* Markdown content */}
        <div className="prose prose-sm dark:prose-invert max-w-none text-sm [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {message.content}
          </ReactMarkdown>
        </div>

        {/* Streaming indicator */}
        {isStreaming && (
          <span className="inline-block w-2 h-4 bg-sra-accent animate-pulse rounded-sm ml-0.5" />
        )}

        {/* Citations */}
        {message.citations.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {message.citations.map((cit, i) => (
              <CitationBadge
                key={i}
                citation={cit}
                onClick={() => onCitationClick?.(cit)}
              />
            ))}
          </div>
        )}

        {/* Confidence bar — always shown for assistant messages */}
        {confidence && <ConfidenceBar confidence={confidence} />}

        {/* Flagged claims */}
        {flaggedClaims && flaggedClaims.length > 0 && (
          <FlaggedClaims flaggedClaims={flaggedClaims} />
        )}

        {/* Alternative interpretations */}
        {alternatives && alternatives.length > 0 && (
          <AlternativePanel alternatives={alternatives} />
        )}

        {/* Footer: timestamp + pin */}
        <div className="flex items-center gap-2 mt-1 opacity-0 group-hover:opacity-60 transition-opacity">
          <span className="text-[10px] text-sra-muted">{ts}</span>
          {onPin && !isStreaming && (
            <button
              onClick={() => onPin(message.content, message.citations)}
              className="text-sra-muted hover:text-sra-accent transition-colors"
              title="Pin this finding"
            >
              <Pin size={12} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
