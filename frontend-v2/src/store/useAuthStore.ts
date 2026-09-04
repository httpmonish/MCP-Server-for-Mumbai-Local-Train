import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import type { SuburbanLineCode, CollegeInfo, DemoStudentProfile, AttendanceRecord } from "../types";

export const MUMBAI_COLLEGES: CollegeInfo[] = [
  {
    id: "vjti",
    name: "Veermata Jijabai Technological Institute (VJTI)",
    shortCode: "VJTI",
    location: "Matunga, Mumbai",
    nearestStation: "Matunga",
    defaultLine: "CR",
    portalUrl: "https://erp.vjti.ac.in",
    campusCode: "MU_STANDARD",
  },
  {
    id: "spit",
    name: "Sardar Patel Institute of Technology (SPIT)",
    shortCode: "SPIT",
    location: "Andheri West, Mumbai",
    nearestStation: "Andheri",
    defaultLine: "WR",
    portalUrl: "https://spit.edu.in/portal",
    campusCode: "MU_STANDARD",
  },
  {
    id: "djsce",
    name: "Dwarkadas J. Sanghvi College of Engineering (DJSCE)",
    shortCode: "DJSCE",
    location: "Vile Parle West, Mumbai",
    nearestStation: "Vile Parle",
    defaultLine: "WR",
    portalUrl: "https://djsce.ac.in/erp",
    campusCode: "MU_STANDARD",
  },
  {
    id: "kjsce",
    name: "K.J. Somaiya College of Engineering (KJSCE)",
    shortCode: "KJSCE",
    location: "Vidyavihar East, Mumbai",
    nearestStation: "Vidyavihar",
    defaultLine: "CR",
    portalUrl: "https://somaiya.edu/kjsce/portal",
    campusCode: "MU_STANDARD",
  },
  {
    id: "tsec",
    name: "Thadomal Shahani Engineering College (TSEC)",
    shortCode: "TSEC",
    location: "Bandra West, Mumbai",
    nearestStation: "Bandra",
    defaultLine: "WR",
    portalUrl: "https://tsec.edu/portal",
    campusCode: "MU_STANDARD",
  },
  {
    id: "mu_standard",
    name: "University of Mumbai (Standard ERP)",
    shortCode: "MU ERP",
    location: "Kalina, Santacruz / Fort",
    nearestStation: "Kurla",
    defaultLine: "CR",
    portalUrl: "https://mu.ac.in/academic-portal",
    campusCode: "MU_STANDARD",
  },
];

export const DEMO_PROFILES: DemoStudentProfile[] = [
  {
    id: "demo-borderline",
    name: "Aarav Sharma",
    rollNo: "241635",
    collegeId: "vjti",
    department: "Computer Engineering (SE)",
    standingCategory: "borderline",
    homeStation: "Kasara",
    attendanceData: [
      { subject_name: "Advanced Computer Networks", total_conducted: 42, total_attended: 32, percentage: 76.2 },
      { subject_name: "Database Management Systems", total_conducted: 38, total_attended: 24, percentage: 63.2 },
      { subject_name: "Operating Systems", total_conducted: 40, total_attended: 31, percentage: 77.5 },
      { subject_name: "Software Engineering Lab", total_conducted: 34, total_attended: 23, percentage: 67.6 },
    ],
  },
  {
    id: "demo-critical",
    name: "Pooja Patel",
    rollNo: "231042",
    collegeId: "spit",
    department: "Information Technology (TE)",
    standingCategory: "critical",
    homeStation: "Virar",
    attendanceData: [
      { subject_name: "Distributed Computing & Cloud", total_conducted: 42, total_attended: 24, percentage: 57.1 },
      { subject_name: "Machine Learning Foundations", total_conducted: 40, total_attended: 25, percentage: 62.5 },
      { subject_name: "Cyber Security & Cryptography", total_conducted: 38, total_attended: 26, percentage: 68.4 },
      { subject_name: "DevOps & Cloud Architecture", total_conducted: 34, total_attended: 20, percentage: 58.8 },
    ],
  },
  {
    id: "demo-safe",
    name: "Rohan Kulkarni",
    rollNo: "221890",
    collegeId: "kjsce",
    department: "Electronics & Telecomm (BE)",
    standingCategory: "safe",
    homeStation: "Thane",
    attendanceData: [
      { subject_name: "Embedded IoT & Robotics", total_conducted: 42, total_attended: 38, percentage: 90.5 },
      { subject_name: "Digital Signal Processing", total_conducted: 40, total_attended: 35, percentage: 87.5 },
      { subject_name: "VLSI System Design", total_conducted: 38, total_attended: 33, percentage: 86.8 },
      { subject_name: "Wireless Communication", total_conducted: 36, total_attended: 31, percentage: 86.1 },
    ],
  },
];

interface AuthState {
  studentId: string;
  username: string;
  password: string;
  fromStation: string;
  toStation: string;
  selectedLine: SuburbanLineCode;
  trainTypeFilter: string;
  selectedCollegeId: string;
  activeProfileId: string;
  customAttendanceOverride: AttendanceRecord[] | null;
  setStudentId: (id: string) => void;
  setCredentials: (username: string, password: string) => void;
  setRoute: (from: string, to: string) => void;
  swapRoute: () => void;
  setSelectedLine: (line: SuburbanLineCode) => void;
  setTrainTypeFilter: (filter: string) => void;
  setSelectedCollegeId: (id: string) => void;
  loadDemoProfile: (profileId: string) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      studentId: "241635",
      username: "aarav.sharma",
      password: "••••••••",
      fromStation: "Matunga",
      toStation: "Kasara",
      selectedLine: "CR",
      trainTypeFilter: "ALL",
      selectedCollegeId: "vjti",
      activeProfileId: "demo-borderline",
      customAttendanceOverride: DEMO_PROFILES[0].attendanceData,

      setStudentId: (id) => set({ studentId: id }),
      setCredentials: (username, password) =>
        set({ username, password, customAttendanceOverride: null }),
      setRoute: (from, to) => set({ fromStation: from, toStation: to }),
      swapRoute: () => {
        const { fromStation, toStation } = get();
        set({ fromStation: toStation, toStation: fromStation });
      },
      setSelectedLine: (line) => set({ selectedLine: line }),
      setTrainTypeFilter: (filter) => set({ trainTypeFilter: filter }),

      setSelectedCollegeId: (id) => {
        const college = MUMBAI_COLLEGES.find((c) => c.id === id);
        if (college) {
          set({
            selectedCollegeId: id,
            fromStation: college.nearestStation,
            selectedLine: college.defaultLine,
          });
        } else {
          set({ selectedCollegeId: id });
        }
      },

      loadDemoProfile: (profileId) => {
        const profile = DEMO_PROFILES.find((p) => p.id === profileId);
        if (profile) {
          const college = MUMBAI_COLLEGES.find((c) => c.id === profile.collegeId);
          set({
            studentId: profile.rollNo,
            username: profile.name.toLowerCase().replace(/\s+/g, "."),
            activeProfileId: profile.id,
            selectedCollegeId: profile.collegeId,
            fromStation: college?.nearestStation || "CSMT",
            toStation: profile.homeStation,
            selectedLine: college?.defaultLine || "CR",
            customAttendanceOverride: profile.attendanceData,
          });
        }
      },

      clearAuth: () =>
        set({
          studentId: "",
          username: "",
          password: "",
          customAttendanceOverride: null,
          activeProfileId: "custom",
        }),
    }),
    {
      name: "campus-commute-auth-v2",
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        studentId: state.studentId,
        username: state.username,
        fromStation: state.fromStation,
        toStation: state.toStation,
        selectedLine: state.selectedLine,
        trainTypeFilter: state.trainTypeFilter,
        selectedCollegeId: state.selectedCollegeId,
        activeProfileId: state.activeProfileId,
      }),
    }
  )
);
