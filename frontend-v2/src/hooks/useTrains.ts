import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../api/client";
import type { LineInfo, NetworkHealth, StationItem, TrainQueryResponse } from "../types";
import { useAuthStore } from "../store/useAuthStore";

export function useNextTrains() {
  const { fromStation, toStation, selectedLine, trainTypeFilter } = useAuthStore();

  return useQuery({
    queryKey: ["trains", fromStation, toStation, selectedLine, trainTypeFilter],
    queryFn: async () => {
      const params = new URLSearchParams({
        from_station: fromStation,
        to_station: toStation,
        limit: "8",
      });
      if (selectedLine && selectedLine !== "ALL") {
        params.append("line", selectedLine);
      }
      if (trainTypeFilter && trainTypeFilter !== "ALL") {
        params.append("train_type", trainTypeFilter);
      }
      return apiClient<TrainQueryResponse>(`/api/v1/trains/next?${params.toString()}`);
    },
    enabled: Boolean(fromStation && toStation && fromStation !== toStation),
    refetchInterval: 30000, // 30s background poll
    staleTime: 15000,
  });
}

export function useTrainLines() {
  return useQuery({
    queryKey: ["trainLines"],
    queryFn: async () => {
      return apiClient<{ lines: LineInfo[] }>("/api/v1/trains/lines");
    },
    staleTime: 1000 * 60 * 60, // 1 hour
  });
}

export function useTrainStations(line?: string) {
  return useQuery({
    queryKey: ["trainStations", line || "ALL"],
    queryFn: async () => {
      const url = line && line !== "ALL" ? `/api/v1/trains/stations?line=${line}` : "/api/v1/trains/stations";
      return apiClient<{ line: string; count: number; stations: StationItem[] }>(url);
    },
    staleTime: 1000 * 60 * 60,
  });
}

export function useNetworkStatus() {
  return useQuery({
    queryKey: ["networkStatus"],
    queryFn: async () => {
      return apiClient<NetworkHealth>("/api/v1/trains/status");
    },
    refetchInterval: 60000,
    staleTime: 30000,
  });
}

