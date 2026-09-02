import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../api/client";
import type { TrainQueryResponse } from "../types";
import { useAuthStore } from "../store/useAuthStore";

export function useNextTrains() {
  const { fromStation, toStation } = useAuthStore();

  return useQuery({
    queryKey: ["trains", fromStation, toStation],
    queryFn: async () => {
      return apiClient<TrainQueryResponse>(
        `/api/v1/trains/next?from_station=${encodeURIComponent(
          fromStation
        )}&to_station=${encodeURIComponent(toStation)}&limit=4`
      );
    },
    enabled: Boolean(fromStation && toStation && fromStation !== toStation),
    refetchInterval: 30000, // 30s background poll
    staleTime: 15000,
  });
}
