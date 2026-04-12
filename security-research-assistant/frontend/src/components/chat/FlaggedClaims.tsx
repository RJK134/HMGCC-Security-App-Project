/** Expandable warning section for unverified claims. */

import { AlertTriangle, ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";

interface Props {
  flaggedClaims: string[];
}

export function FlaggedClaims({ flaggedClaims }: Props) {
  const [expanded, setExpanded] = useState(false);

  if (!flaggedClaims.length) return null;

  return (
    <div className="mt-2 border border-amber-300 dark:border-amber-700 rounded-lg bg-amber-50 dark:bg-amber-900/20">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 w-full px-3 py-1.5 text-left text-xs font-medium text-amber-700 dark:text-amber-300"
      >
        <AlertTriangle size={14} />
        <span>{flaggedClaims.length} claim{flaggedClaims.length > 1 ? "s" : ""} could not be verified</span>
        {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
      </button>

      {expanded && (
        <ul className="px-3 pb-2 space-y-1">
          {flaggedClaims.map((claim, i) => (
            <li key={i} className="text-xs text-amber-600 dark:text-amber-400 pl-5">
              &bull; {claim}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
