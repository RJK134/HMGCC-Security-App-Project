/** Health check hook — polls backend every 30 seconds. */

import { useQuery } from "@tanstack/react-query";
import { healthCheck } from "../api/client";
import type { HealthStatus } from "../types";

export function useHealth() {
  return useQuery<HealthStatus>({
    queryKey: ["health"],
    queryFn: healthCheck,
    refetchInterval: 10_000,
    retry: 2,
    staleTime: 5_000,
  });
}
