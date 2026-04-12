/** Visual confidence score bar with expandable explanation. */

import { AlertTriangle, ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";
import type { ConfidenceResult } from "../../types";

function scoreColor(score: number): string {
  if (score >= 81) return "bg-green-500";
  if (score >= 61) return "bg-green-400";
  if (score >= 31) return "bg-amber-400";
  return "bg-red-500";
}

function scoreLabel(score: number): string {
  if (score >= 81) return "High";
  if (score >= 61) return "Good";
  if (score >= 31) return "Medium";
  return "Low";
}

interface Props {
  confidence: ConfidenceResult;
}

export function ConfidenceBar({ confidence }: Props) {
  const [expanded, setExpanded] = useState(false);
  const { score, explanation } = confidence;

  return (
    <div className="mt-2 border-t border-sra-border pt-2">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 w-full text-left"
      >
        {/* Bar */}
        <div className="flex-1 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden max-w-[120px]">
          <div
            className={`h-full rounded-full transition-all ${scoreColor(score)}`}
            style={{ width: `${score}%` }}
          />
        </div>

        <span className="text-xs font-medium">{score.toFixed(0)}/100</span>
        <span className="text-[10px] text-sra-muted">{scoreLabel(score)}</span>

        {score < 40 && (
          <AlertTriangle size={12} className="text-amber-500" />
        )}

        {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
      </button>

      {expanded && (
        <p className="text-xs text-sra-muted mt-1 pl-1">{explanation}</p>
      )}

      {score < 40 && (
        <p className="text-[10px] text-amber-500 mt-1">
          Low confidence — consider importing additional source documents.
        </p>
      )}
    </div>
  );
}
