import React, { useEffect, useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { AttendanceCard } from "./components/AttendanceCard";
import { TrainTrackerCard } from "./components/TrainTrackerCard";
import { useAuthStore } from "./store/useAuthStore";
import { useNetworkStatus } from "./hooks/useTrains";
import {
  CheckCircle2,
  Clock,
  GraduationCap,
  KeyRound,
  Train,
} from "lucide-react";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
    },
  },
});

export const Dashboard: React.FC = () => {
  const { studentId, username, setStudentId, setCredentials } = useAuthStore();
  const [showConfig, setShowConfig] = useState(!studentId);
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 via-slate-50 to-indigo-50/30 text-slate-800 antialiased">
      {/* Network Status Ticker Banner */}
      <div className="bg-slate-900 text-slate-200 text-xs px-4 py-2 border-b border-slate-800 shadow-inner">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
            </span>
            <span className="font-extrabold text-[11px] uppercase tracking-wider text-slate-400">
              Mumbai Suburban Network Live:
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-4 text-[11px]">
            {/* Central Line */}
            <div className="flex items-center gap-1.5 font-medium">
              <span className="w-2 h-2 rounded-full bg-rose-500" />
              <span className="font-bold text-white">Central (CR):</span>
              <span className="text-emerald-400 font-semibold">
                {networkStatus?.lines?.CR?.status || "On Time"}
              </span>
              <span className="text-slate-400">({networkStatus?.lines?.CR?.punctuality || "98.2%"})</span>
            </div>

            {/* Western Line */}
            <div className="flex items-center gap-1.5 font-medium">
              <span className="w-2 h-2 rounded-full bg-blue-500" />
              <span className="font-bold text-white">Western (WR):</span>
              <span className="text-emerald-400 font-semibold">
                {networkStatus?.lines?.WR?.status || "On Time"}
              </span>
              <span className="text-slate-400">({networkStatus?.lines?.WR?.punctuality || "99.1%"})</span>
            </div>

            {/* Harbour Line */}
            <div className="flex items-center gap-1.5 font-medium">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              <span className="font-bold text-white">Harbour (HR):</span>
              <span className="text-emerald-400 font-semibold">
                {networkStatus?.lines?.HR?.status || "Normal"}
              </span>
              <span className="text-slate-400">({networkStatus?.lines?.HR?.punctuality || "97.8%"})</span>
            </div>
          </div>

          <div className="hidden md:flex items-center gap-1 text-[11px] text-slate-400 font-mono">
            <Clock className="w-3.5 h-3.5 text-indigo-400" />
            <span>IST {currentTime}</span>
          </div>
        </div>
      </div>

      {/* Main Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-slate-200/80 sticky top-0 z-30 px-6 py-3.5 transition-all">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-700 to-purple-600 flex items-center justify-center text-white shadow-md shadow-indigo-200">
              <Train className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-black text-slate-900 tracking-tight">
                  Campus & Commute
                </h1>
                <span className="text-[10px] bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-extrabold px-2 py-0.5 rounded-full uppercase tracking-wider shadow-sm">
                  v2.5 Dynamic
                </span>
              </div>
              <p className="text-xs text-slate-500 font-medium">
                Mumbai Suburban Railway Tracker & University Academic Dashboard
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowConfig(!showConfig)}
              className="flex items-center gap-1.5 text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 px-3.5 py-2 rounded-xl border border-slate-300/80 font-bold transition-all shadow-sm active:scale-95"
            >
              <KeyRound className="w-3.5 h-3.5 text-slate-500" />
              {showConfig ? "Hide Config" : studentId ? "Portal: " + studentId : "Set Credentials"}
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-7xl mx-auto p-4 sm:p-6 space-y-6">
        {showConfig && (
          <form
            onSubmit={handleSave}
            className="bg-white/90 backdrop-blur-sm p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-wrap gap-4 items-end transition-all"
          >
            <div className="flex-1 min-w-[200px]">
              <label className="text-xs font-bold text-slate-600 uppercase tracking-wider flex items-center gap-1">
                <GraduationCap className="w-3.5 h-3.5 text-indigo-600" /> Student Roll / ID
              </label>
              <input
                type="text"
                required
                value={tempId}
                onChange={(e) => setTempId(e.target.value)}
                placeholder="e.g. 241635"
                className="w-full mt-1.5 p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm font-medium outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
              />
            </div>
            <div className="flex-1 min-w-[200px]">
              <label className="text-xs font-bold text-slate-600 uppercase tracking-wider">Portal Username</label>
              <input
                type="text"
                required
                value={tempUser}
                onChange={(e) => setTempUser(e.target.value)}
                placeholder="portal username"
                className="w-full mt-1.5 p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm font-medium outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
              />
            </div>
            <div className="flex-1 min-w-[200px]">
              <label className="text-xs font-bold text-slate-600 uppercase tracking-wider">Portal Password</label>
              <input
                type="password"
                required
                value={tempPass}
                onChange={(e) => setTempPass(e.target.value)}
                placeholder="••••••••"
                className="w-full mt-1.5 p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm font-medium outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
              />
            </div>
            <button
              type="submit"
              className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-sm px-6 py-2.5 rounded-xl shadow-md shadow-indigo-200 transition-all active:scale-95 flex items-center gap-1.5"
            >
              <CheckCircle2 className="w-4 h-4" /> Save & Sync
            </button>
          </form>
        )}

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <TrainTrackerCard />
          <AttendanceCard />
        </div>
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
