/** TanStack Query hooks for document operations. */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import * as api from "../api/client";
import type { SourceTier } from "../types";

export function useDocuments(projectId: string | null) {
  return useQuery({
    queryKey: ["documents", projectId],
    queryFn: () => api.listDocuments(projectId!),
    enabled: !!projectId,
    staleTime: 10_000,
  });
}

export function useDocument(id: string | null) {
  return useQuery({
    queryKey: ["document", id],
    queryFn: () => api.getDocument(id!),
    enabled: !!id,
  });
}

export function useUploadDocument() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      projectId,
      file,
      tier,
    }: {
      projectId: string;
      file: File;
      tier?: SourceTier;
    }) => api.uploadDocument(projectId, file, tier),
    onSuccess: (_, vars) =>
      qc.invalidateQueries({ queryKey: ["documents", vars.projectId] }),
  });
}

export function useDeleteDocument() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.deleteDocument(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["documents"] }),
  });
}

export function useUpdateDocumentTier() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, tier }: { id: string; tier: SourceTier }) =>
      api.updateDocumentTier(id, tier),
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ["documents"] });
      qc.invalidateQueries({ queryKey: ["document", vars.id] });
    },
  });
}
