import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

interface AuthState {
  studentId: string;
  username: string;
  password: string;
  fromStation: string;
  toStation: string;
  setStudentId: (id: string) => void;
  setCredentials: (username: string, password: string) => void;
  setRoute: (from: string, to: string) => void;
  swapRoute: () => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      studentId: "",
      username: "",
      password: "",
      fromStation: "Thane",
      toStation: "Byculla",
      setStudentId: (id) => set({ studentId: id }),
      setCredentials: (username, password) => set({ username, password }),
      setRoute: (from, to) => set({ fromStation: from, toStation: to }),
      swapRoute: () => {
        const { fromStation, toStation } = get();
        set({ fromStation: toStation, toStation: fromStation });
      },
      clearAuth: () => set({ studentId: "", username: "", password: "" }),
    }),
    {
      name: "campus-commute-auth",
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        studentId: state.studentId,
        username: state.username,
        // Omit cleartext password from long-term localStorage if desired,
        // or encrypt/retain in session memory
        fromStation: state.fromStation,
        toStation: state.toStation,
      }),
    }
  )
);
