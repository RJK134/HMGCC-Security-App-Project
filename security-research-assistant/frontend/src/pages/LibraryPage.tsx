/** Document library page — drop zone, toolbar, grid/list views. */

import { Grid3x3, List, Search } from "lucide-react";
import { useMemo, useState } from "react";
import { DropZone } from "../components/library/DropZone";
import { DocumentGrid } from "../components/library/DocumentGrid";
import { DocumentList } from "../components/library/DocumentList";
import { useDocuments } from "../hooks/useDocuments";
import { useAppStore } from "../stores/appStore";
import type { DocumentMetadata, DocumentType, SourceTier } from "../types";

type ViewMode = "grid" | "list";
type SortBy = "name" | "date" | "size" | "type";

export function LibraryPage() {
  const { currentProjectId } = useAppStore();
  const { data, refetch } = useDocuments(currentProjectId);

  const [viewMode, setViewMode] = useState<ViewMode>("grid");
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState<DocumentType | "all">("all");
  const [tierFilter, setTierFilter] = useState<SourceTier | "all">("all");
  const [sortBy, setSortBy] = useState<SortBy>("date");

  const documents: DocumentMetadata[] = data?.documents ?? [];
  const totalDocuments: number = (data as Record<string, unknown>)?.total as number ?? documents.length;

  const filtered = useMemo(() => {
    let result = documents;

    // Search
    if (search) {
      const q = search.toLowerCase();
      result = result.filter((d) => d.filename.toLowerCase().includes(q));
    }

    // Type filter
    if (typeFilter !== "all") {
      result = result.filter((d) => d.filetype === typeFilter);
    }

    // Tier filter
    if (tierFilter !== "all") {
      result = result.filter((d) => d.source_tier === tierFilter);
    }

    // Sort
    result = [...result].sort((a, b) => {
      switch (sortBy) {
        case "name": return a.filename.localeCompare(b.filename);
        case "date": return b.import_timestamp.localeCompare(a.import_timestamp);
        case "size": return b.size_bytes - a.size_bytes;
        case "type": return a.filetype.localeCompare(b.filetype);
        default: return 0;
      }
    });

    return result;
  }, [documents, search, typeFilter, tierFilter, sortBy]);

  if (!currentProjectId) {
    return (
      <div className="h-full flex items-center justify-center">
        <p className="text-sra-muted">Select a project to view its document library.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Drop zone */}
      <DropZone onImportComplete={() => refetch()} />

      {/* Toolbar */}
      <div className="flex items-center gap-3 flex-wrap">
        {/* Search */}
        <div className="relative flex-1 min-w-[200px] max-w-[300px]">
          <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-sra-muted" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search files..."
            className="w-full pl-8 pr-3 py-1.5 text-xs rounded-lg border border-sra-border bg-transparent focus:ring-1 focus:ring-sra-accent focus:outline-none"
          />
        </div>

        {/* Type filter */}
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value as DocumentType | "all")}
          className="text-xs px-2 py-1.5 rounded-lg border border-sra-border bg-transparent focus:ring-1 focus:ring-sra-accent focus:outline-none"
        >
          <option value="all">All Types</option>
          <option value="pdf">PDF</option>
          <option value="image">Image</option>
          <option value="code">Code</option>
          <option value="text">Text</option>
          <option value="spreadsheet">Spreadsheet</option>
        </select>

        {/* Tier filter */}
        <select
          value={tierFilter}
          onChange={(e) => setTierFilter(e.target.value as SourceTier | "all")}
          className="text-xs px-2 py-1.5 rounded-lg border border-sra-border bg-transparent focus:ring-1 focus:ring-sra-accent focus:outline-none"
        >
          <option value="all">All Tiers</option>
          <option value="tier_1_manufacturer">Manufacturer</option>
          <option value="tier_2_academic">Academic</option>
          <option value="tier_3_trusted_forum">Trusted Forum</option>
          <option value="tier_4_unverified">Unverified</option>
        </select>

        {/* Sort */}
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as SortBy)}
          className="text-xs px-2 py-1.5 rounded-lg border border-sra-border bg-transparent focus:ring-1 focus:ring-sra-accent focus:outline-none"
        >
          <option value="date">Date imported</option>
          <option value="name">Name</option>
          <option value="size">Size</option>
          <option value="type">Type</option>
        </select>

        {/* View toggle */}
        <div className="flex border border-sra-border rounded-lg overflow-hidden ml-auto">
          <button
            onClick={() => setViewMode("grid")}
            className={`p-1.5 ${viewMode === "grid" ? "bg-sra-accent/10 text-sra-accent" : "text-sra-muted"}`}
            title="Grid view"
          >
            <Grid3x3 size={14} />
          </button>
          <button
            onClick={() => setViewMode("list")}
            className={`p-1.5 ${viewMode === "list" ? "bg-sra-accent/10 text-sra-accent" : "text-sra-muted"}`}
            title="List view"
          >
            <List size={14} />
          </button>
        </div>
      </div>

      {/* Document count */}
      <p className="text-xs text-sra-muted">
        Showing {filtered.length} of {totalDocuments} documents
      </p>

      {/* Documents view */}
      {viewMode === "grid" ? (
        <DocumentGrid documents={filtered} />
      ) : (
        <DocumentList documents={filtered} />
      )}
    </div>
  );
}
