/** Drag-and-drop file import zone with upload queue. */

import { CheckCircle, CloudUpload, Loader2, XCircle } from "lucide-react";
import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { uploadDocument } from "../../api/client";
import { useAppStore } from "../../stores/appStore";
import type { SourceTier } from "../../types";
import { SourceTierSelector } from "./SourceTierSelector";

const ACCEPT_EXTENSIONS =
  ".pdf,.png,.jpg,.jpeg,.tiff,.tif,.bmp,.c,.h,.cpp,.py,.asm,.s,.rs,.go,.java,.sh,.txt,.md,.html,.xml,.json,.csv,.xlsx";

interface FileStatus {
  file: File;
  status: "pending" | "uploading" | "done" | "error";
  error?: string;
}

interface Props {
  onImportComplete?: () => void;
}

export function DropZone({ onImportComplete }: Props) {
  const { currentProjectId } = useAppStore();
  const [tier, setTier] = useState<SourceTier>("tier_4_unverified");
  const [files, setFiles] = useState<FileStatus[]>([]);
  const [importing, setImporting] = useState(false);

  const processQueue = useCallback(
    async (fileList: FileStatus[]) => {
      if (!currentProjectId) return;
      setImporting(true);

      for (let i = 0; i < fileList.length; i++) {
        setFiles((prev) =>
          prev.map((f, idx) => (idx === i ? { ...f, status: "uploading" } : f)),
        );
        try {
          await uploadDocument(currentProjectId, fileList[i].file, tier);
          setFiles((prev) =>
            prev.map((f, idx) => (idx === i ? { ...f, status: "done" } : f)),
          );
        } catch (err) {
          setFiles((prev) =>
            prev.map((f, idx) =>
              idx === i
                ? { ...f, status: "error", error: err instanceof Error ? err.message : "Upload failed" }
                : f,
            ),
          );
        }
      }

      setImporting(false);
      onImportComplete?.();
    },
    [currentProjectId, tier, onImportComplete],
  );

  const onDrop = useCallback(
    (accepted: File[]) => {
      const newFiles: FileStatus[] = accepted.map((file) => ({
        file,
        status: "pending",
      }));
      setFiles(newFiles);
      processQueue(newFiles);
    },
    [processQueue],
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "image/*": [".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"],
      "text/*": [".txt", ".md", ".html", ".xml", ".json", ".csv", ".c", ".h", ".cpp", ".py", ".asm", ".s"],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
    },
    disabled: !currentProjectId,
  });

  const doneCount = files.filter((f) => f.status === "done").length;
  const errorCount = files.filter((f) => f.status === "error").length;

  return (
    <div className="space-y-3">
      {/* Drop target */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all ${
          isDragActive
            ? "border-sra-accent bg-sra-accent/5"
            : "border-sra-border hover:border-gray-400 dark:hover:border-gray-500"
        } ${!currentProjectId ? "opacity-50 cursor-not-allowed" : ""}`}
      >
        <input {...getInputProps()} />
        <CloudUpload size={32} className="mx-auto text-sra-muted mb-2" />
        {isDragActive ? (
          <p className="text-sm font-medium text-sra-accent">Drop files to import</p>
        ) : (
          <>
            <p className="text-sm font-medium">Drag files here or click to browse</p>
            <p className="text-xs text-sra-muted mt-1">
              PDF, images, code, text, spreadsheets
            </p>
          </>
        )}
      </div>

      {/* Tier selector */}
      <div className="flex items-center gap-3">
        <span className="text-xs text-sra-muted">Source quality:</span>
        <SourceTierSelector value={tier} onChange={setTier} size="sm" />
      </div>

      {/* File list during import */}
      {files.length > 0 && (
        <div className="border border-sra-border rounded-lg divide-y divide-sra-border max-h-48 overflow-y-auto">
          {files.map((f, i) => (
            <div key={i} className="flex items-center gap-2 px-3 py-1.5 text-xs">
              {f.status === "uploading" && <Loader2 size={14} className="animate-spin text-sra-accent" />}
              {f.status === "done" && <CheckCircle size={14} className="text-green-500" />}
              {f.status === "error" && <XCircle size={14} className="text-red-500" />}
              {f.status === "pending" && <span className="w-3.5 h-3.5 rounded-full bg-gray-300" />}
              <span className="truncate flex-1">{f.file.name}</span>
              <span className="text-sra-muted">{(f.file.size / 1024).toFixed(0)} KB</span>
            </div>
          ))}
        </div>
      )}

      {/* Summary */}
      {files.length > 0 && !importing && (
        <p className="text-xs text-sra-muted">
          {doneCount} imported{errorCount > 0 ? `, ${errorCount} failed` : ""}
          <button
            onClick={() => setFiles([])}
            className="ml-2 text-sra-accent hover:underline"
          >
            Clear
          </button>
        </p>
      )}
    </div>
  );
}
