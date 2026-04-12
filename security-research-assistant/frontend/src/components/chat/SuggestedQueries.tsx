/** Clickable follow-up query suggestions below the latest assistant message. */

interface Props {
  suggestions: string[];
  onSelect: (query: string) => void;
}

export function SuggestedQueries({ suggestions, onSelect }: Props) {
  if (!suggestions.length) return null;

  return (
    <div className="flex flex-wrap gap-2 mt-2 ml-2">
      {suggestions.map((q, i) => (
        <button
          key={i}
          onClick={() => onSelect(q)}
          className="text-xs px-3 py-1.5 rounded-full border border-sra-accent/30 text-sra-accent hover:bg-sra-accent/10 transition-colors"
        >
          {q}
        </button>
      ))}
    </div>
  );
}
