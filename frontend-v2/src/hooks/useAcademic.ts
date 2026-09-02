import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../api/client";
import type { AttendanceResponse, ExamResponse } from "../types";
import { useAuthStore } from "../store/useAuthStore";

export function useAttendance() {
  const { studentId, username, password } = useAuthStore();

  return useQuery({
    queryKey: ["academic", "attendance", studentId],
    queryFn: async () => {
      return apiClient<AttendanceResponse>(
        `/api/v1/academic/attendance/${studentId}`,
        {
          method: "POST",
          body: JSON.stringify({ username, password }),
        }
      );
    },
    enabled: Boolean(studentId && username && password),
    staleTime: 1000 * 60 * 30, // 30 Minutes
    gcTime: 1000 * 60 * 60 * 2, // 2 Hours
    retry: (failureCount, error: any) => {
      if (error.status === 401 || error.status === 429) return false;
      return failureCount < 2;
    },
  });
}

export function useExams() {
  const { studentId, username, password } = useAuthStore();

  return useQuery({
    queryKey: ["academic", "exams", studentId],
    queryFn: async () => {
      return apiClient<ExamResponse>(
        `/api/v1/academic/exams/${studentId}`,
        {
          method: "POST",
          body: JSON.stringify({ username, password }),
        }
      );
    },
    enabled: Boolean(studentId && username && password),
    staleTime: 1000 * 60 * 60 * 6, // 6 Hours
    gcTime: 1000 * 60 * 60 * 24, // 24 Hours
    retry: 1,
  });
}
