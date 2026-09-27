import React, { useState } from "react";
import { useAttendance } from "../hooks/useAcademic";
import { useAuthStore, MUMBAI_COLLEGES } from "../store/useAuthStore";
import {
  AlertTriangle,
  Building2,
  CheckCircle2,
  Code2,
  Copy,
  Check,
  GraduationCap,
  RefreshCw,
  X,
  BookOpen,
} from "lucide-react";

export const AttendanceCard: React.FC = () => {
  const { data, isLoading, isError, error, refetch, isFetching } = useAttendance();
  const { studentId, username, selectedCollegeId } = useAuthStore();
  const [showRawDbModal, setShowRawDbModal] = useState(false);
  const [copied, setCopied] = useState(false);

  const selectedCollege =
    MUMBAI_COLLEGES.find((c) => c.id === selectedCollegeId) || MUMBAI_COLLEGES[0];

  if (isLoading) {
    return (
      <div className="glass-panel p-6 sm:p-7 animate-pulse space-y-5">
        <div className="flex items-center justify-between">
          <div className="h-6 bg-slate-800 rounded-lg w-1/3"></div>
          <div className="h-6 bg-slate-800 rounded-full w-20"></div>
        </div>
        <div className="h-28 bg-slate-800/60 rounded-2xl"></div>
        <div className="space-y-3">
          <div className="h-12 bg-slate-800/40 rounded-xl"></div>
          <div className="h-12 bg-slate-800/40 rounded-xl"></div>
          <div className="h-12 bg-slate-800/40 rounded-xl"></div>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="glass-panel p-6 sm:p-7 border-rose-500/30 relative overflow-hidden">
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-rose-500 to-amber-500" />
        <div className="flex items-start gap-3">
          <div className="p-2.5 rounded-xl bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Academic ERP Sync Issue</h3>
            <p className="text-xs text-slate-400 mt-1">
              {(error as any)?.detail || "Unable to sync records from academic ERP server."}
            </p>
          </div>
        </div>
        <button
          onClick={() => refetch()}
          className="mt-5 px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white font-medium text-xs rounded-xl shadow-lg shadow-rose-900/30 transition-all active:scale-95 flex items-center gap-2"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Retry ERP Connection
        </button>
      </div>
    );
  }

  const records = data?.data || [];
  const totalConducted = records.reduce((acc, curr) => acc + curr.total_conducted, 0);
  const totalAttended = records.reduce((acc, curr) => acc + curr.total_attended, 0);
  const aggregatePct = totalConducted > 0 ? (totalAttended / totalConducted) * 100 : 0;
  const isCritical = aggregatePct < 75.0;

  // 75% Rule Math Analytics
  const overallNeededTo75 = isCritical
    ? Math.max(1, Math.ceil((0.75 * totalConducted - totalAttended) / 0.25))
    : 0;

  const overallSafeBunk = !isCritical
    ? Math.max(0, Math.floor((totalAttended - 0.75 * totalConducted) / 0.75))
    : 0;

  const rawDbPayload = {
    institute: {
      name: selectedCollege.name,
      code: selectedCollege.shortCode,
      portal_url: selectedCollege.portalUrl,
      db_status: "CONNECTED",
    },
    student: {
      roll_no: studentId || "241635",
      portal_user: username || "student",
      aggregate_percentage: aggregatePct.toFixed(2),
      standing: isCritical ? "DEFICIT (<75%)" : "COMPLIANT (>=75%)",
      lectures_needed_to_75: overallNeededTo75,
      safe_bunk_margin: overallSafeBunk,
    },
    sync_metadata: {
      source: data?.source || "database",
      stale: data?.stale || false,
      last_synced_at: data?.last_synced_at || new Date().toISOString(),
      protocol: "REST / MCP Protocol via FastApi Orchestrator",
    },
    courses: records.map((r) => ({
      subject: r.subject_name,
      conducted: r.total_conducted,
      attended: r.total_attended,
      percentage: r.percentage,
      to_reach_75_needed: r.percentage < 75 ? Math.ceil((0.75 * r.total_conducted - r.total_attended) / 0.25) : 0,
      safe_to_miss: r.percentage >= 75 ? Math.floor((r.total_attended - 0.75 * r.total_conducted) / 0.75) : 0,
    })),
  };

  const handleCopyJson = () => {
    navigator.clipboard.writeText(JSON.stringify(rawDbPayload, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="glass-panel p-6 sm:p-7 flex flex-col justify-between relative overflow-hidden">
      <div>
        {/* Top Header Row */}
        <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center text-white shadow-lg shadow-cyan-900/30">
              <GraduationCap className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-white tracking-tight font-heading">
                  Academic Intelligence
                </h2>
                <span className="text-[11px] font-mono font-semibold px-2 py-0.5 rounded-md bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 flex items-center gap-1">
                  <Building2 className="w-3 h-3" />
                  {selectedCollege.shortCode}
                </span>
              </div>
              <p className="text-xs text-slate-400">
                {selectedCollege.name} ERP Data
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* View Raw JSON / MCP payload */}
            <button
              onClick={() => setShowRawDbModal(true)}
              className="px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 hover:text-white text-xs font-mono font-medium border border-white/10 transition-all flex items-center gap-1.5"
            >
              <Code2 className="w-3.5 h-3.5 text-cyan-400" />
              <span>MCP JSON</span>
            </button>

            {/* Refresh */}
            <button
              onClick={() => refetch()}
              disabled={isFetching}
              title="Sync Academic ERP"
              className="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 hover:text-white border border-white/10 transition-all disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? "animate-spin text-cyan-400" : ""}`} />
            </button>
          </div>
        </div>

        {/* Aggregate Attendance Hero Card */}
        <div className="p-5 rounded-2xl bg-gradient-to-br from-slate-900/90 via-slate-900/50 to-slate-950/90 border border-white/10 mb-5 relative overflow-hidden">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <span className="text-[11px] font-mono font-medium uppercase tracking-wider text-slate-400">
                Aggregate Attendance
              </span>
              <div className="flex items-baseline gap-3 mt-1">
                <span
                  className={`text-3xl sm:text-4xl font-black font-heading tracking-tight ${
                    aggregatePct >= 75
                      ? "text-emerald-400"
                      : aggregatePct >= 65
                      ? "text-amber-400"
                      : "text-rose-400"
                  }`}
                >
                  {aggregatePct.toFixed(1)}%
                </span>
                <span
                  className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${
                    aggregatePct >= 75
                      ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                      : "bg-rose-500/10 text-rose-400 border-rose-500/30"
                  }`}
                >
                  {aggregatePct >= 75 ? "Compliant (≥75%)" : "Below 75% Criteria"}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1 font-mono">
                {totalAttended} attended of {totalConducted} total lectures
              </p>
            </div>

            {/* 75% Decision Recommendation Pill */}
            <div className="sm:text-right">
              {isCritical ? (
                <div className="inline-flex items-center gap-2 p-3 rounded-xl bg-rose-500/10 border border-rose-500/25 text-rose-300 text-xs text-left">
                  <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0" />
                  <div>
                    <div className="font-semibold text-rose-200">Attend next {overallNeededTo75} lectures</div>
                    <div className="text-[11px] text-rose-400/90">to reach 75.0% threshold</div>
                  </div>
                </div>
              ) : (
                <div className="inline-flex items-center gap-2 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/25 text-emerald-300 text-xs text-left">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                  <div>
                    <div className="font-semibold text-emerald-200">{overallSafeBunk} lectures safe to miss</div>
                    <div className="text-[11px] text-emerald-400/90">while staying ≥75%</div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Overall Progress Bar */}
          <div className="mt-4 w-full bg-slate-800/80 h-2.5 rounded-full overflow-hidden p-0.5 border border-white/5 relative">
            <div
              className={`h-full rounded-full transition-all duration-700 ${
                aggregatePct >= 75
                  ? "bg-gradient-to-r from-emerald-500 to-teal-400"
                  : aggregatePct >= 65
                  ? "bg-gradient-to-r from-amber-500 to-yellow-400"
                  : "bg-gradient-to-r from-rose-600 to-rose-400"
              }`}
              style={{ width: `${Math.min(100, Math.max(5, aggregatePct))}%` }}
            />
            {/* 75% target marker */}
            <div
              className="absolute top-0 bottom-0 w-0.5 bg-white/70"
              style={{ left: "75%" }}
              title="75% Statutory Limit"
            />
          </div>
        </div>

        {/* Subject-by-Subject List */}
        <div>
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400 mb-3 uppercase tracking-wider font-mono">
            <span className="flex items-center gap-1.5">
              <BookOpen className="w-3.5 h-3.5 text-cyan-400" /> Course Breakdown
            </span>
            <span>Target: 75%</span>
          </div>

          <div className="space-y-2.5">
            {records.map((course, idx) => {
              const isLow = course.percentage < 75;
              const lecturesNeeded = isLow
                ? Math.ceil((0.75 * course.total_conducted - course.total_attended) / 0.25)
                : 0;

              return (
                <div
                  key={course.subject_name || idx}
                  className="p-3.5 rounded-xl bg-slate-900/60 hover:bg-slate-850/80 border border-white/5 hover:border-white/15 transition-all"
                >
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span className="text-xs font-semibold text-slate-200 truncate">
                      {course.subject_name}
                    </span>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <span className="text-xs font-mono font-bold text-slate-300">
                        {course.percentage.toFixed(1)}%
                      </span>
                      <span
                        className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                          isLow
                            ? "bg-rose-500/15 text-rose-400 border border-rose-500/30"
                            : "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                        }`}
                      >
                        {course.total_attended}/{course.total_conducted}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="flex-1 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          course.percentage >= 75
                            ? "bg-emerald-500"
                            : course.percentage >= 65
                            ? "bg-amber-500"
                            : "bg-rose-500"
                        }`}
                        style={{ width: `${Math.min(100, Math.max(3, course.percentage))}%` }}
                      />
                    </div>
                    {isLow && (
                      <span className="text-[10px] font-mono text-amber-400/90 whitespace-nowrap">
                        +{lecturesNeeded} needed
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Raw MCP JSON Modal */}
      {showRawDbModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md">
          <div className="glass-panel w-full max-w-2xl max-h-[85vh] flex flex-col border-cyan-500/30 shadow-2xl">
            <div className="flex items-center justify-between p-4 sm:p-5 border-b border-white/10">
              <div className="flex items-center gap-2">
                <Code2 className="w-5 h-5 text-cyan-400" />
                <h3 className="text-sm font-bold text-white font-heading">
                  Model Context Protocol (MCP) · Live Academic Schema
                </h3>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleCopyJson}
                  className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-mono font-medium flex items-center gap-1.5 transition-all"
                >
                  {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copied ? "Copied" : "Copy JSON"}</span>
                </button>
                <button
                  onClick={() => setShowRawDbModal(false)}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-all"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="p-4 overflow-y-auto flex-1 font-mono text-xs text-cyan-300/90 bg-slate-950/80 rounded-b-2xl">
              <pre className="whitespace-pre-wrap leading-relaxed">
                {JSON.stringify(rawDbPayload, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
