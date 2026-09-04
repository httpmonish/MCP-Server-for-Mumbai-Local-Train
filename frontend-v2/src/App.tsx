import React, { useEffect, useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { AttendanceCard } from "./components/AttendanceCard";
import { TrainTrackerCard } from "./components/TrainTrackerCard";
import { RunningTrainBackground } from "./components/RunningTrainBackground";
import { useAuthStore, MUMBAI_COLLEGES, DEMO_PROFILES } from "./store/useAuthStore";
import { useNetworkStatus } from "./hooks/useTrains";
import {
  CheckCircle2,
  Clock,
  GraduationCap,
  KeyRound,
  Radio,
  Train,
  Zap,
  Building2,
  UserCheck,
} from "lucide-react";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
    },
  },
});

export const Dashboard: React.FC = () => {
  const {
    studentId,
    username,
    selectedLine,
    selectedCollegeId,
    activeProfileId,
    setStudentId,
    setCredentials,
    setSelectedCollegeId,
    loadDemoProfile,
  } = useAuthStore();

  const [showConfig, setShowConfig] = useState(false);
  const [tempId, setTempId] = useState(studentId);
  const [tempUser, setTempUser] = useState(username);
  const [tempPass, setTempPass] = useState("");
  const [currentTime, setCurrentTime] = useState(new Date().toLocaleTimeString());

  const { data: networkStatus } = useNetworkStatus();

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString());
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setStudentId(tempId);
    setCredentials(tempUser, tempPass);
    setShowConfig(false);
  };

  const selectedCollege =
    MUMBAI_COLLEGES.find((c) => c.id === selectedCollegeId) || MUMBAI_COLLEGES[0];

  return (
    <div className="min-h-screen relative overflow-x-hidden text-slate-800 antialiased font-sans">
      {/* 1. Authentic Mumbai Local EMU & Parallax Track Background */}
      <RunningTrainBackground />

      {/* 2. Top Network Signal & Live Telemetry Ticker (Frosted Slate) */}
      <div className="relative z-20 bg-slate-900/95 backdrop-blur-md text-slate-200 text-xs px-4 py-2 border-b border-slate-800 shadow-xs">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <span className="flex h-2.5 w-2.5 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500 shadow-[0_0_8px_#10B981]" />
            </span>
            <span className="font-mono font-bold text-[11px] tracking-wider text-slate-300 flex items-center gap-1.5">
              <Radio className="w-3.5 h-3.5 text-emerald-400" />
              SUBURBAN RADAR LIVE
            </span>
            <span className="hidden sm:inline-block font-hand text-sm text-emerald-300 font-bold ml-1">
              (Central Kasara • Western • Harbour synced)
            </span>
          </div>

          {/* Line Telemetry Metrics */}
          <div className="flex flex-wrap items-center gap-4 text-[11px] font-mono">
            {/* Central Line */}
            <div className="flex items-center gap-1.5 bg-slate-800/90 px-2.5 py-0.5 rounded-lg border border-slate-700">
              <span className="w-2 h-2 rounded-full bg-rose-500 shadow-[0_0_6px_#F43F5E]" />
              <span className="font-bold text-white">CR:</span>
              <span className="text-emerald-400 font-semibold">
                {networkStatus?.lines?.CR?.status || "On Time"}
              </span>
              <span className="text-slate-400">({networkStatus?.lines?.CR?.punctuality || "98.2%"})</span>
            </div>

            {/* Western Line */}
            <div className="flex items-center gap-1.5 bg-slate-800/90 px-2.5 py-0.5 rounded-lg border border-slate-700">
              <span className="w-2 h-2 rounded-full bg-blue-500 shadow-[0_0_6px_#3B82F6]" />
              <span className="font-bold text-white">WR:</span>
              <span className="text-emerald-400 font-semibold">
                {networkStatus?.lines?.WR?.status || "On Time"}
              </span>
              <span className="text-slate-400">({networkStatus?.lines?.WR?.punctuality || "99.1%"})</span>
            </div>

            {/* Harbour Line */}
            <div className="flex items-center gap-1.5 bg-slate-800/90 px-2.5 py-0.5 rounded-lg border border-slate-700">
              <span className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_6px_#10B981]" />
              <span className="font-bold text-white">HR:</span>
              <span className="text-emerald-400 font-semibold">
                {networkStatus?.lines?.HR?.status || "Normal"}
              </span>
              <span className="text-slate-400">({networkStatus?.lines?.HR?.punctuality || "97.8%"})</span>
            </div>
          </div>

          <div className="hidden lg:flex items-center gap-2 text-[11px] font-mono text-slate-300">
            <Clock className="w-3.5 h-3.5 text-indigo-400" />
            <span className="bg-slate-800 px-2 py-0.5 rounded border border-slate-700">IST {currentTime}</span>
          </div>
        </div>
      </div>

      {/* 3. Executive Command Header with Glassmorphism */}
      <header className="relative z-20 bg-white/90 backdrop-blur-xl border-b border-slate-200/90 sticky top-0 px-4 sm:px-8 py-3.5 shadow-xs transition-all">
        <div className="max-w-7xl mx-auto flex flex-wrap justify-between items-center gap-4">
          <div className="flex items-center gap-3.5">
            {/* Logo Emblem with Mumbai EMU icon */}
            <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-slate-900 via-slate-800 to-indigo-950 flex items-center justify-center text-white shadow-md shadow-slate-300/60 border border-slate-700/40 relative overflow-hidden group">
              <Train className="w-5 h-5 text-indigo-200 group-hover:scale-110 transition-transform" />
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700" />
            </div>

            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-black text-slate-900 tracking-tight">
                  Campus & Commute
                </h1>
                <span className="text-[10px] bg-slate-900 text-white font-mono font-bold px-2 py-0.5 rounded-md uppercase tracking-wider">
                  OPS-DESK
                </span>
                <span className="hidden md:inline-block font-hand text-base text-rose-600 font-bold -rotate-1">
                  Today's m-Indicator Master Run Sheet ✍️
                </span>
              </div>
              <p className="text-xs text-slate-500 font-medium flex items-center gap-2">
                <span>Mumbai Suburban Railway Network (CSMT • Kasara • Churchgate • Virar • Panvel)</span>
                <span className="hidden sm:inline text-slate-300">•</span>
                <span className="hidden sm:inline font-blueprint text-slate-600 text-xs font-semibold">
                  Scale: 1:1 Live Telemetry
                </span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Active Corridor Indicator Pill */}
            <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 rounded-xl border border-slate-200 text-xs font-mono font-bold text-slate-700 shadow-2xs">
              <Zap className="w-3.5 h-3.5 text-amber-500 animate-pulse" />
              <span>CORRIDOR: {selectedLine === "ALL" ? "MULTI-LINE" : `${selectedLine}`}</span>
            </div>

            {/* Custom DB Login Trigger */}
            <button
              onClick={() => setShowConfig(!showConfig)}
              className="flex items-center gap-2 text-xs bg-slate-900 hover:bg-slate-800 text-white px-4 py-2 rounded-xl font-bold transition-all shadow-sm active:scale-95 border border-slate-800"
            >
              <KeyRound className="w-3.5 h-3.5 text-indigo-300" />
              <span>{showConfig ? "Close Credentials" : studentId ? `Roll: ${studentId}` : "Set Custom DB"}</span>
            </button>
          </div>
        </div>
      </header>

      {/* 4. Main Dashboard Workspace */}
      <main className="relative z-10 max-w-7xl mx-auto p-4 sm:p-6 lg:p-8 space-y-6">
        {/* COLLEGE / INSTITUTE SELECTION & RAW DATA PROFILE SWITCHER BAR */}
        <div className="bg-white/95 backdrop-blur-xl p-4 sm:p-5 rounded-3xl border border-slate-200 shadow-lg space-y-4">
          {/* Top Row: College Selector */}
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <Building2 className="w-4 h-4 text-indigo-600" />
              <span className="text-xs font-black uppercase tracking-wider text-slate-700 font-mono">
                Select Institute / College Database:
              </span>
            </div>

            <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium">
              <span>Nearest Station:</span>
              <span className="font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-md border border-indigo-200 font-mono">
                {selectedCollege.nearestStation} ({selectedCollege.defaultLine})
              </span>
            </div>
          </div>

          {/* College Pills Row */}
          <div className="flex flex-wrap items-center gap-2">
            {MUMBAI_COLLEGES.map((col) => {
              const isSelected = col.id === selectedCollegeId;
              return (
                <button
                  key={col.id}
                  onClick={() => setSelectedCollegeId(col.id)}
                  className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all border ${
                    isSelected
                      ? "bg-slate-900 text-white border-slate-900 shadow-sm"
                      : "bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100 hover:text-slate-900"
                  }`}
                >
                  <span>{col.shortCode}</span>
                  <span className="ml-1 opacity-70 text-[10px] hidden sm:inline">({col.location.split(",")[0]})</span>
                </button>
              );
            })}
          </div>

          {/* Bottom Row: Pre-loaded Demo Student Profiles with Raw Data */}
          <div className="pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <UserCheck className="w-4 h-4 text-emerald-600" />
              <span className="text-xs font-black uppercase tracking-wider text-slate-700 font-mono">
                Load Student Dataset Profile:
              </span>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              {DEMO_PROFILES.map((p) => {
                const isActive = p.id === activeProfileId;
                const statusColor =
                  p.standingCategory === "borderline"
                    ? "text-amber-700 bg-amber-50 border-amber-300"
                    : p.standingCategory === "critical"
                    ? "text-rose-700 bg-rose-50 border-rose-300"
                    : "text-emerald-700 bg-emerald-50 border-emerald-300";

                return (
                  <button
                    key={p.id}
                    onClick={() => loadDemoProfile(p.id)}
                    className={`px-3 py-1 rounded-xl text-xs font-bold transition-all border flex items-center gap-1.5 ${
                      isActive
                        ? "bg-indigo-600 text-white border-indigo-600 shadow-xs"
                        : `${statusColor} hover:brightness-95`
                    }`}
                  >
                    <span>{p.name}</span>
                    <span className="text-[10px] font-mono opacity-80 uppercase">
                      ({p.standingCategory})
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Kasara Corridor Operational Notice */}
        <div className="flex flex-wrap items-center justify-between gap-3 bg-gradient-to-r from-amber-50/90 via-white/90 to-slate-50/90 backdrop-blur-md p-4 rounded-2xl border border-amber-200 shadow-xs">
          <div className="flex items-center gap-3">
            <div className="w-2 h-8 bg-amber-500 rounded-full" />
            <div>
              <div className="font-hand text-lg text-slate-800 font-bold leading-tight flex items-center gap-2">
                <span>Central Railway update: Kasara corridor 37 stations topology active</span>
                <span className="text-xs font-mono font-normal bg-amber-100 text-amber-900 px-2 py-0.5 rounded-md">
                  m-Indicator v2026.09
                </span>
              </div>
              <p className="text-xs font-blueprint text-slate-600">
                Train numbers 95401–95435 Fast & 96402/96406 Slow locals operating with live buffer matching
              </p>
            </div>
          </div>
          <div className="font-mono text-[11px] text-slate-500 hidden sm:block">
            STAMP: CR-ENG-VERIFIED // <span className="font-hand text-slate-700 font-bold text-sm">Approved ✍️</span>
          </div>
        </div>

        {/* Expandable Custom Portal Configuration Form */}
        {showConfig && (
          <form
            onSubmit={handleSave}
            className="bg-white/95 backdrop-blur-xl p-6 rounded-3xl border border-slate-200 shadow-xl transition-all relative overflow-hidden"
          >
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-rose-500" />

            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-base font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
                  <GraduationCap className="w-5 h-5 text-indigo-600" />
                  Connect Custom College ERP Credentials
                </h3>
                <p className="text-xs text-slate-500 font-medium">
                  Connect your live Mumbai University ERP credentials for automated attendance sync
                </p>
              </div>
              <div className="font-hand text-sm text-slate-500 hidden md:block">
                &ldquo;AES-256 encrypted zero-trust local storage&rdquo;
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-xs font-bold text-slate-600 uppercase tracking-wider flex items-center justify-between">
                  <span>Student ID / Roll No</span>
                  <span className="font-hand text-xs text-slate-400">e.g. 241635</span>
                </label>
                <input
                  type="text"
                  required
                  value={tempId}
                  onChange={(e) => setTempId(e.target.value)}
                  placeholder="241635"
                  className="w-full mt-1.5 p-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-semibold outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all shadow-2xs"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-slate-600 uppercase tracking-wider flex items-center justify-between">
                  <span>Portal Username</span>
                  <span className="font-hand text-xs text-slate-400">ERP Login</span>
                </label>
                <input
                  type="text"
                  required
                  value={tempUser}
                  onChange={(e) => setTempUser(e.target.value)}
                  placeholder="student username"
                  className="w-full mt-1.5 p-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-semibold outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all shadow-2xs"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-slate-600 uppercase tracking-wider flex items-center justify-between">
                  <span>Password</span>
                  <span className="font-hand text-xs text-slate-400">Secret key</span>
                </label>
                <input
                  type="password"
                  required
                  value={tempPass}
                  onChange={(e) => setTempPass(e.target.value)}
                  placeholder="••••••••"
                  className="w-full mt-1.5 p-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-semibold outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all shadow-2xs"
                />
              </div>
            </div>

            <div className="mt-5 pt-4 border-t border-slate-100 flex flex-wrap justify-between items-center gap-3">
              <div className="flex items-center gap-2 text-xs text-slate-500 font-mono">
                <span className="w-2 h-2 rounded-full bg-indigo-500" />
                <span>ACTIVE ADAPTER: {selectedCollege.name} ({selectedCollege.campusCode})</span>
              </div>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setShowConfig(false)}
                  className="px-4 py-2.5 text-xs font-bold text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 rounded-xl transition-all"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs px-6 py-2.5 rounded-xl shadow-md shadow-indigo-200 transition-all active:scale-95 flex items-center gap-1.5"
                >
                  <CheckCircle2 className="w-4 h-4" /> Save Credentials & Sync Live DB
                </button>
              </div>
            </div>
          </form>
        )}

        {/* 5. Core Dashboard Grid: Train Tracker & Academic Standings */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8 items-start">
          <TrainTrackerCard />
          <AttendanceCard />
        </div>

        {/* 6. Engineering Footer with Blueprint Notation & Hand-signed Seal */}
        <footer className="pt-8 pb-12 text-center text-slate-400 border-t border-slate-300/40">
          <div className="flex flex-wrap items-center justify-center gap-6 text-xs font-mono mb-2">
            <span>MUMBAI SUBURBAN NETWORK • CR / WR / HR</span>
            <span>•</span>
            <span>KASARA SECTION: 37 STATIONS VERIFIED</span>
            <span>•</span>
            <span className="font-hand text-slate-600 font-bold text-sm">
              Design & Topology Handcrafted for Daily Commuters 🚆
            </span>
          </div>
          <p className="text-[11px] text-slate-400 font-blueprint">
            Autonomous Commute & Campus Model Context Protocol Engine • v2.5
          </p>
        </footer>
      </main>
    </div>
  );
};

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Dashboard />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
