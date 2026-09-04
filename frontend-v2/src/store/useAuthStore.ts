import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import type { SuburbanLineCode } from "../types";

interface AuthState {
  studentId: string;
  username: string;
  password: string;
  fromStation: string;
  toStation: string;
  selectedLine: SuburbanLineCode;
  trainTypeFilter: string;
  setStudentId: (id: string) => void;
  setCredentials: (username: string, password: string) => void;
  setRoute: (from: string, to: string) => void;
  swapRoute: () => void;
  setSelectedLine: (line: SuburbanLineCode) => void;
  setTrainTypeFilter: (filter: string) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      studentId: "",
      username: "",
      password: "",
      fromStation: "CSMT",
      toStation: "Thane",
      selectedLine: "ALL",
      trainTypeFilter: "ALL",
      setStudentId: (id) => set({ studentId: id }),
      setCredentials: (username, password) => set({ username, password }),
      setRoute: (from, to) => set({ fromStation: from, toStation: to }),
      swapRoute: () => {
        const { fromStation, toStation } = get();
        set({ fromStation: toStation, toStation: fromStation });
      },
      setSelectedLine: (line) => set({ selectedLine: line }),
      setTrainTypeFilter: (filter) => set({ trainTypeFilter: filter }),
      clearAuth: () => set({ studentId: "", username: "", password: "" }),
    }),
    {
      name: "campus-commute-auth",
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        studentId: state.studentId,
        username: state.username,
        fromStation: state.fromStation,
        toStation: state.toStation,
        selectedLine: state.selectedLine,
        trainTypeFilter: state.trainTypeFilter,
      }),
    }
  )
);

