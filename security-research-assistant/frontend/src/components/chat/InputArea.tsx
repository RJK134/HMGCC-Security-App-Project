/** Chat input area with multi-line support and keyboard shortcuts. */

import { ArrowUp, Square } from "lucide-react";
import { useCallback, useRef, useState, type KeyboardEvent } from "react";

interface Props {
  onSend: (text: string) => void;
  onCancel?: () => void;
  isStreaming: boolean;
  disabled?: boolean;
}

export function InputArea({ onSend, onCancel, isStreaming, disabled }: Props) {
  const [text, setText] = useState("");
  const ref = useRef<HTMLTextAreaElement>(null);

  const handleSend = useCallback(() => {
    const trimmed = text.trim();
    if (!trimmed || isStreaming || disabled) return;
    onSend(trimmed);
    setText("");
    // Reset textarea height
    if (ref.current) ref.current.style.height = "auto";
  }, [text, isStreaming, disabled, onSend]);

  const handleKey = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend],
  );

  const handleInput = useCallback(() => {
    const el = ref.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 160) + "px"; // Max ~6 lines
  }, []);

  return (
    <div className="border-t border-sra-border bg-sra-sidebar p-3">
      <div className="flex items-end gap-2 max-w-4xl mx-auto">
        <textarea
          ref={ref}
          value={text}
          onChange={(e) => { setText(e.target.value); handleInput(); }}
          onKeyDown={handleKey}
          placeholder="Ask a question about your documents..."
          rows={1}
          className="flex-1 resize-none rounded-xl border border-sra-border bg-sra-bg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-sra-accent/50 placeholder:text-sra-muted overflow-y-auto"
          style={{ maxHeight: 160 }}
          disabled={disabled}
        />

        {isStreaming ? (
          <button
            onClick={onCancel}
            className="shrink-0 w-10 h-10 flex items-center justify-center rounded-xl bg-red-500 text-white hover:bg-red-600 transition-colors"
            title="Stop generating"
          >
            <Square size={16} />
          </button>
        ) : (
          <button
            onClick={handleSend}
            disabled={!text.trim() || disabled}
            className="shrink-0 w-10 h-10 flex items-center justify-center rounded-xl bg-sra-accent text-white hover:opacity-90 transition-opacity disabled:opacity-30 disabled:cursor-not-allowed"
            title="Send message (Enter)"
          >
            <ArrowUp size={18} />
          </button>
        )}
      </div>

      <p className="text-[10px] text-sra-muted text-center mt-1.5">
        Responses are grounded in your imported documents
      </p>
    </div>
  );
}
