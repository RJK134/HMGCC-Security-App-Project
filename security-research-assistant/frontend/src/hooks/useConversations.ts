/** TanStack Query hooks for conversation management. */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import * as api from "../api/client";

export function useConversations(projectId: string | null) {
  return useQuery({
    queryKey: ["conversations", projectId],
    queryFn: () => api.listConversations(projectId!),
    enabled: !!projectId,
    staleTime: 10_000,
  });
}

export function useConversation(id: string | null) {
  return useQuery({
    queryKey: ["conversation", id],
    queryFn: () => api.getConversation(id!),
    enabled: !!id,
  });
}

export function useCreateConversation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ projectId, title }: { projectId: string; title: string }) =>
      api.createConversation(projectId, title),
    onSuccess: (_, vars) =>
      qc.invalidateQueries({ queryKey: ["conversations", vars.projectId] }),
  });
}

export function useDeleteConversation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.deleteConversation(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["conversations"] }),
  });
}
