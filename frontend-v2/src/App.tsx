import React, { useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { AttendanceCard } from "./components/AttendanceCard";
import { TrainTrackerCard } from "./components/TrainTrackerCard";
import { useAuthStore } from "./store/useAuthStore";

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

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setStudentId(tempId);
    setCredentials(tempUser, tempPass);
    setShowConfig(false);
  };

  return (
    <div className="min-h-screen bg-slate-100 text-slate-800">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10 px-6 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">
            Campus & Commute <span className="text-indigo-600 text-xs px-2 py-0.5 bg-indigo-50 rounded-full font-bold uppercase">v2</span>
          </h1>
          <p className="text-xs text-slate-500">Suburban transit & attendance command center</p>
        </div>
        <button
          onClick={() => setShowConfig(!showConfig)}
          className="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded-lg border border-slate-300 font-medium transition-colors"
        >
          {showConfig ? "Close Credentials" : "Configure Credentials"}
        </button>
      </header>

      {/* Main Container */}
      <main className="max-w-7xl mx-auto p-6 space-y-6">
        {showConfig && (
          <form onSubmit={handleSave} className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-wrap gap-4 items-end">
            <div className="flex-1 min-w-[200px]">
              <label className="text-xs font-bold text-slate-600 uppercase">Student Roll / ID</label>
              <input
                type="text"
                required
                value={tempId}
                onChange={(e) => setTempId(e.target.value)}
                placeholder="241635"
                className="w-full mt-1 p-2 bg-slate-50 border border-slate-200 rounded text-sm outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div className="flex-1 min-w-[200px]">
              <label className="text-xs font-bold text-slate-600 uppercase">Portal Username</label>
              <input
                type="text"
                required
                value={tempUser}
                onChange={(e) => setTempUser(e.target.value)}
                placeholder="username"
                className="w-full mt-1 p-2 bg-slate-50 border border-slate-200 rounded text-sm outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div className="flex-1 min-w-[200px]">
              <label className="text-xs font-bold text-slate-600 uppercase">Portal Password</label>
              <input
                type="password"
                required
                value={tempPass}
                onChange={(e) => setTempPass(e.target.value)}
                placeholder="••••••••"
                className="w-full mt-1 p-2 bg-slate-50 border border-slate-200 rounded text-sm outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <button
              type="submit"
              className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm px-5 py-2.5 rounded-lg transition-colors"
            >
              Save Credentials
            </button>
          </form>
        )}

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <AttendanceCard/>
          <TrainTrackerCard/>
        </div>
      </main>
    </div>
  );
};

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Dashboard/>
      <ReactQueryDevtools initialIsOpen={false}/>
    </QueryClientProvider>
  );
}
