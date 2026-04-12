/** Inline clickable citation badge — colour-coded by source tier. */

import type { Citation, SourceTier } from "../../types";

const TIER_BG: Record<string, string> = {
  tier_1_manufacturer: "bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300",
  tier_2_academic: "bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300",
  tier_3_trusted_forum: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-300",
  tier_4_unverified: "bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400",
};

interface Props {
  citation: Citation;
  tier?: SourceTier;
  onClick: () => void;
}

export function CitationBadge({ citation, tier, onClick }: Props) {
  const bg = TIER_BG[tier ?? "tier_4_unverified"] ?? TIER_BG.tier_4_unverified;
  const name =
    citation.document_name.length > 25
      ? citation.document_name.slice(0, 22) + "..."
      : citation.document_name;

  return (
    <button
      onClick={onClick}
      className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[11px] font-medium ${bg} hover:opacity-80 transition-opacity cursor-pointer`}
      title={`${citation.document_name}${citation.page_number ? `, Page ${citation.page_number}` : ""}\nRelevance: ${(citation.relevance_score * 100).toFixed(0)}%\n${citation.excerpt.slice(0, 120)}`}
    >
      <span>{name}</span>
      {citation.page_number != null && (
        <span className="opacity-70">p.{citation.page_number}</span>
      )}
    </button>
  );
}
