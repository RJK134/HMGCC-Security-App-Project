/** Expandable panel for alternative interpretations. */

import { ChevronDown, ChevronUp, Lightbulb } from "lucide-react";
import { useState } from "react";

interface Props {
  alternatives: string[];
}

export function AlternativePanel({ alternatives }: Props) {
  const [expanded, setExpanded] = useState(false);

  if (!alternatives.length) return null;

  return (
    <div className="mt-2 border border-blue-200 dark:border-blue-800 rounded-lg bg-blue-50 dark:bg-blue-900/20">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 w-full px-3 py-1.5 text-left text-xs font-medium text-blue-700 dark:text-blue-300"
      >
        <Lightbulb size={14} />
        <span>Alternative interpretations</span>
        {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
      </button>

      {expanded && (
        <ul className="px-3 pb-2 space-y-1">
          {alternatives.map((alt, i) => (
            <li key={i} className="text-xs text-blue-600 dark:text-blue-400 pl-5">
              &bull; {alt}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
