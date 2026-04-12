/** Reusable source quality tier selector with colour-coded badges. */

import type { SourceTier } from "../../types";

const TIERS: { value: SourceTier; label: string; color: string; tip: string }[] = [
  { value: "tier_1_manufacturer", label: "Manufacturer", color: "bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300 border-blue-300 dark:border-blue-700", tip: "Official datasheets, manuals, specification sheets" },
  { value: "tier_2_academic", label: "Academic", color: "bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300 border-green-300 dark:border-green-700", tip: "IEEE/IEC standards, peer-reviewed papers" },
  { value: "tier_3_trusted_forum", label: "Trusted Forum", color: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-300 border-yellow-300 dark:border-yellow-700", tip: "Stack Overflow, known expert blogs" },
  { value: "tier_4_unverified", label: "Unverified", color: "bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400 border-gray-300 dark:border-gray-600", tip: "Unverified forum posts, unknown sources" },
];

interface Props {
  value: SourceTier;
  onChange: (tier: SourceTier) => void;
  size?: "sm" | "md";
}

export function SourceTierSelector({ value, onChange, size = "md" }: Props) {
  const textSize = size === "sm" ? "text-[10px]" : "text-xs";
  const pad = size === "sm" ? "px-1.5 py-0.5" : "px-2 py-1";

  return (
    <div className="flex flex-wrap gap-1">
      {TIERS.map((t) => (
        <button
          key={t.value}
          onClick={() => onChange(t.value)}
          title={t.tip}
          className={`${pad} ${textSize} rounded-full border font-medium transition-all ${
            value === t.value
              ? `${t.color} ring-1 ring-offset-1 ring-sra-accent`
              : "border-sra-border text-sra-muted hover:border-gray-400"
          }`}
        >
          {t.label}
        </button>
      ))}
    </div>
  );
}

/** Badge-only display of a source tier (non-interactive). */
export function TierBadge({ tier, size = "sm" }: { tier: SourceTier; size?: "sm" | "md" }) {
  const t = TIERS.find((x) => x.value === tier) ?? TIERS[3];
  const cls = size === "sm" ? "text-[10px] px-1.5 py-0.5" : "text-xs px-2 py-0.5";
  return (
    <span className={`${cls} rounded-full font-medium ${t.color}`} title={t.tip}>
      {t.label}
    </span>
  );
}
