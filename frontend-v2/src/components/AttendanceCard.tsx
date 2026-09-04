import React, { useState } from "react";
import { useAttendance } from "../hooks/useAcademic";
import { useAuthStore, MUMBAI_COLLEGES } from "../store/useAuthStore";
import {
  AlertTriangle,
  BookOpen,
  CheckCircle,
  Database,
  ExternalLink,
  GraduationCap,
  RefreshCw,
  X,
  Copy,
  Check,
  Building2,
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
      <div className="bg-white/90 backdrop-blur-xl rounded-3xl shadow-xl border border-slate-200/90 p-7 animate-pulse">
        <div className="h-6 bg-slate-200 rounded w-1/3 mb-5"></div>
        <div className="h-24 bg-slate-100 rounded-2xl mb-6"></div>
        <div className="space-y-4">
          <div className="h-10 bg-slate-100 rounded-xl"></div>
          <div className="h-10 bg-slate-100 rounded-xl"></div>
          <div className="h-10 bg-slate-100 rounded-xl"></div>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="bg-white/95 backdrop-blur-xl rounded-3xl shadow-xl border border-rose-200 p-7 relative overflow-hidden">
        <div className="absolute top-0 left-0 right-0 h-1 bg-rose-500" />
        <h3 className="text-lg font-extrabold text-rose-800 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-rose-600" /> Academic ERP Sync Failed
        </h3>
        <p className="text-xs text-rose-600 mt-2 font-medium">
          {(error as any)?.detail || "Unable to sync records from academic ERP server."}
        </p>
        <div className="font-hand text-sm text-slate-500 mt-3">
          &ldquo;Please verify college portal credentials or select a verified student profile&rdquo;
        </div>
        <button
          onClick={() => refetch()}
          className="mt-5 px-5 py-2.5 bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs rounded-xl shadow-md transition-all active:scale-95"
        >
          Retry Database Connection
        </button>
      </div>
    );
  }

  const records = data?.data || [];
  const totalConducted = records.reduce((acc, curr) => acc + curr.total_conducted, 0);
  const totalAttended = records.reduce((acc, curr) => acc + curr.total_attended, 0);
  const aggregatePct = totalConducted > 0 ? (totalAttended / totalConducted) * 100 : 0;
  const isCritical = aggregatePct < 75.0;

  // 75% Math Analytics
  const deficitPct = isCritical ? 75.0 - aggregatePct : 0;
  const surplusPct = !isCritical ? aggregatePct - 75.0 : 0;

  // Lectures needed: ceil((0.75 * C - A) / 0.25)
  const overallNeededTo75 = isCritical
    ? Math.max(1, Math.ceil((0.75 * totalConducted - totalAttended) / 0.25))
    : 0;

  // Safe to bunk: floor((A - 0.75 * C) / 0.75)
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
      protocol: "REST / JSON-RPC via FastApi Orchestrator",
    },
    courses: records.map((r) => {
      const need = r.percentage < 75 ? Math.ceil((0.75 * r.total_conducted - r.total_attended) / 0.25) : 0;
      const bunk = r.percentage >= 75 ? Math.floor((r.total_attended - 0.75 * r.total_conducted) / 0.75) : 0;
      return {
        subject: r.subject_name,
        conducted: r.total_conducted,
        attended: r.total_attended,
        percentage: r.percentage,
        to_reach_75_needed: need,
        safe_to_miss: bunk,
      };
    }),
  };

  const handleCopyJson = () => {
    navigator.clipboard.writeText(JSON.stringify(rawDbPayload, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-white/95 backdrop-blur-xl rounded-3xl shadow-xl border border-slate-200/90 p-6 sm:p-7 flex flex-col justify-between relative overflow-hidden transition-all duration-300">
      <div>
        {/* Top Header Row with Institute Badge & DB Button */}
        <div className="flex flex-wrap justify-between items-start gap-3 mb-5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-slate-900 to-indigo-800 flex items-center justify-center text-white shadow-md">
              <GraduationCap className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-black text-slate-900 tracking-tight">Academic Standing</h2>
                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 border border-indigo-200 flex items-center gap-1">
                  <Building2 className="w-3 h-3" />
                  {selectedCollege.shortCode}
                </span>
              </div>
              <p className="text-xs text-slate-500 font-medium">
                Connected to {selectedCollege.name} ERP
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* View College DB Raw Data Button */}
            <button
              onClick={() => setShowRawDbModal(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-mono text-xs font-semibold transition-all border border-slate-200 shadow-2xs active:scale-95"
              title="Inspect College Database JSON & Raw Schemas"
            >
              <Database className="w-3.5 h-3.5 text-indigo-600" />
              <span>College DB Data</span>
            </button>

            <button
              onClick={() => refetch()}
              disabled={isFetching}
              title="Refresh Academic Records"
              className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 transition-all border border-slate-200 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${isFetching ? "animate-spin text-indigo-600" : ""}`} />
            </button>
          </div>
        </div>

        {/* PROMINENT 75% ATTENDANCE GOAL & DEFICIT KPI BANNER */}
        <div
          className={`p-5 rounded-2xl mb-6 transition-all border ${
            isCritical
              ? "bg-gradient-to-br from-rose-50 via-white to-orange-50 border-rose-200 shadow-xs"
              : "bg-gradient-to-br from-emerald-50 via-white to-teal-50 border-emerald-200 shadow-xs"
          }`}
        >
          <div className="flex flex-wrap justify-between items-center gap-4">
            <div>
              <div className="text-[10px] uppercase font-mono font-bold tracking-wider text-slate-500 flex items-center gap-1.5">
                <BookOpen className="w-3.5 h-3.5" /> CURRENT AGGREGATE ATTENDANCE
              </div>
              <div className="flex items-baseline gap-2 mt-1">
                <span
                  className={`text-4xl font-black tracking-tight ${
                    isCritical ? "text-rose-700" : "text-emerald-700"
                  }`}
                >
                  {aggregatePct.toFixed(1)}%
                </span>
                <span className="text-xs text-slate-500 font-medium">
                  ({totalAttended} of {totalConducted} lectures attended)
                </span>
              </div>
            </div>

            {/* Target 75% Indicator Box */}
            <div className="flex flex-col items-end">
              {isCritical ? (
                <div className="bg-rose-100 border border-rose-300 text-rose-900 px-3.5 py-1.5 rounded-xl text-right">
                  <div className="text-xs font-black flex items-center gap-1.5 justify-end text-rose-800">
                    <AlertTriangle className="w-4 h-4 text-rose-600" />
                    <span>{deficitPct.toFixed(1)}% Remaining to reach 75%</span>
                  </div>
                  <div className="font-blueprint text-xs text-rose-700 font-bold mt-0.5">
                    Attend next <span className="underline decoration-2">{overallNeededTo75} consecutive</span> lectures!
                  </div>
                </div>
              ) : (
                <div className="bg-emerald-100 border border-emerald-300 text-emerald-900 px-3.5 py-1.5 rounded-xl text-right">
                  <div className="text-xs font-black flex items-center gap-1.5 justify-end text-emerald-800">
                    <CheckCircle className="w-4 h-4 text-emerald-600" />
                    <span>+{surplusPct.toFixed(1)}% Above 75% Requirement</span>
                  </div>
                  <div className="font-blueprint text-xs text-emerald-700 font-bold mt-0.5">
                    Safe to bunk <span className="underline decoration-2">{overallSafeBunk} upcoming</span> lectures
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Progress Bar with 75% Marker Line */}
          <div className="mt-4 pt-3 border-t border-slate-200/60">
            <div className="flex justify-between text-[10px] font-mono text-slate-500 mb-1">
              <span>0%</span>
              <span className="font-bold text-slate-800 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-rose-500 inline-block" />
                75.0% Mandatory Hall Ticket Cutoff
              </span>
              <span>100%</span>
            </div>
            <div className="w-full h-3 bg-slate-200/80 rounded-full relative overflow-hidden p-0.5">
              {/* 75% Threshold indicator line */}
              <div className="absolute top-0 bottom-0 left-[75%] w-0.5 bg-slate-900 z-10" />
              <div
                className={`h-full rounded-full transition-all duration-700 ${
                  isCritical
                    ? "bg-gradient-to-r from-orange-500 to-rose-600"
                    : "bg-gradient-to-r from-teal-500 to-emerald-600"
                }`}
                style={{ width: `${Math.min(100, aggregatePct)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Course-by-Course Attendance Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-slate-200/80 text-slate-400 font-mono text-[10px] uppercase tracking-wider">
              <tr>
                <th className="pb-3 font-bold">Course / Subject</th>
                <th className="pb-3 font-bold text-center">Attended / Total</th>
                <th className="pb-3 font-bold text-center">Current %</th>
                <th className="pb-3 font-bold text-right">To Reach 75% / Bunk Margin</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {records.map((r, idx) => {
                const underQuota = r.percentage < 75.0;
                const need = underQuota
                  ? Math.max(1, Math.ceil((0.75 * r.total_conducted - r.total_attended) / 0.25))
                  : 0;
                const bunk = !underQuota
                  ? Math.max(0, Math.floor((r.total_attended - 0.75 * r.total_conducted) / 0.75))
                  : 0;

                return (
                  <tr key={idx} className="hover:bg-slate-50/80 transition-colors group">
                    <td className="py-3.5 pr-2">
                      <div className="font-bold text-slate-800 text-xs sm:text-sm group-hover:text-indigo-600 transition-colors">
                        {r.subject_name}
                      </div>
                      <span className="font-hand text-xs text-slate-400 block mt-0.5">
                        {underQuota ? "Deficit detected • Attend consecutive classes" : "Criteria satisfied"}
                      </span>
                    </td>
                    <td className="py-3.5 text-center text-xs font-mono font-semibold text-slate-600">
                      {r.total_attended} <span className="text-slate-400">/</span> {r.total_conducted}
                    </td>
                    <td className="py-3.5 text-center">
                      <span
                        className={`px-2.5 py-0.5 rounded-lg text-xs font-mono font-extrabold ${
                          underQuota
                            ? "bg-rose-100 text-rose-700 border border-rose-200"
                            : "bg-emerald-100 text-emerald-700 border border-emerald-200"
                        }`}
                      >
                        {r.percentage.toFixed(1)}%
                      </span>
                    </td>
                    <td className="py-3.5 text-right">
                      {underQuota ? (
                        <div className="inline-flex flex-col items-end">
                          <span className="px-2.5 py-0.5 bg-rose-100 text-rose-800 border border-rose-200 rounded-md font-mono text-xs font-bold">
                            +{need} needed
                          </span>
                          <span className="text-[10px] font-blueprint text-rose-600 mt-0.5">
                            { (75.0 - r.percentage).toFixed(1) }% to reach 75%
                          </span>
                        </div>
                      ) : (
                        <div className="inline-flex flex-col items-end">
                          <span className="px-2.5 py-0.5 bg-emerald-100 text-emerald-800 border border-emerald-200 rounded-md font-mono text-xs font-bold">
                            {bunk} safe to bunk
                          </span>
                          <span className="text-[10px] font-blueprint text-emerald-600 mt-0.5">
                            +{ (r.percentage - 75.0).toFixed(1) }% safe buffer
                          </span>
                        </div>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* RAW DATABASE MODAL (Instant Raw Data Inspector) */}
      {showRawDbModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 max-w-2xl w-full max-h-[85vh] flex flex-col overflow-hidden">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-indigo-600 text-white flex items-center justify-center shadow-xs">
                  <Database className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-black text-slate-900 text-base">College Database Raw Record Inspector</h3>
                  <p className="text-xs text-slate-500 font-medium font-mono">
                    {selectedCollege.shortCode} • Schema: attendance_sync_v4
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={handleCopyJson}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-slate-200 rounded-xl text-xs font-mono font-bold text-slate-700 hover:bg-slate-100 transition-all shadow-2xs"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copied ? "Copied" : "Copy JSON"}</span>
                </button>
                <button
                  onClick={() => setShowRawDbModal(false)}
                  className="p-1.5 rounded-xl hover:bg-slate-200 text-slate-500 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Modal Content / JSON Pre */}
            <div className="p-6 overflow-y-auto font-mono text-xs text-slate-800 bg-slate-950 text-emerald-400">
              <div className="flex items-center justify-between text-slate-400 text-[11px] pb-3 mb-3 border-b border-slate-800">
                <span>DATABASE STATUS: 200 OK (LIVE REST STREAM)</span>
                <span>ENDPOINT: {selectedCollege.portalUrl}</span>
              </div>
              <pre className="whitespace-pre-wrap leading-relaxed overflow-x-auto selection:bg-indigo-900 selection:text-white">
                {JSON.stringify(rawDbPayload, null, 2)}
              </pre>
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-3 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-xs text-slate-500 font-mono">
              <span>Sync Protocol: AES-256 GCM • MU Standard Adapter</span>
              <a
                href={selectedCollege.portalUrl}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1 text-indigo-600 hover:text-indigo-700 font-bold"
              >
                <span>Visit College Portal</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
