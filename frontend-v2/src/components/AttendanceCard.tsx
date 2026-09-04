import React from "react";
import { useAttendance } from "../hooks/useAcademic";
import {
  AlertTriangle,
  BookOpen,
  CheckCircle,
  Clock,
  GraduationCap,
  RefreshCw,
} from "lucide-react";

export const AttendanceCard: React.FC = () => {
  const { data, isLoading, isError, error, refetch, isFetching } = useAttendance();

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
          <AlertTriangle className="w-5 h-5 text-rose-600" /> Attendance Retrieval Failed
        </h3>
        <p className="text-xs text-rose-600 mt-2 font-medium">
          {(error as any)?.detail || "Unable to sync records from academic ERP server."}
        </p>
        <div className="font-hand text-sm text-slate-500 mt-3">
          &ldquo;Please verify portal credentials in the top configuration panel&rdquo;
        </div>
        <button
          onClick={() => refetch()}
          className="mt-5 px-5 py-2.5 bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs rounded-xl shadow-md transition-all active:scale-95"
        >
          Retry Sync
        </button>
      </div>
    );
  }

  const records = data?.data || [];
  const totalConducted = records.reduce((acc, curr) => acc + curr.total_conducted, 0);
  const totalAttended = records.reduce((acc, curr) => acc + curr.total_attended, 0);
  const aggregatePct = totalConducted > 0 ? (totalAttended / totalConducted) * 100 : 0;
  const isCritical = aggregatePct < 75.0;

  return (
    <div className="bg-white/95 backdrop-blur-xl rounded-3xl shadow-xl border border-slate-200/90 p-6 sm:p-7 flex flex-col justify-between relative overflow-hidden transition-all duration-300">
      {/* Background blueprint alignment marks */}
      <div className="absolute top-3 right-4 font-mono text-[9px] text-slate-300 select-none hidden sm:block">
        [ACAD_MATRIX_SYNCED • REF: MU-ERP]
      </div>

      <div>
        {/* Header with Handwritten note */}
        <div className="flex flex-wrap justify-between items-start gap-3 mb-5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-slate-900 to-indigo-800 flex items-center justify-center text-white shadow-md">
              <GraduationCap className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-black text-slate-900 tracking-tight">Academic Standing</h2>
                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 border border-slate-200">
                  ERP v4.1
                </span>
              </div>
              <p className="text-xs text-slate-500 font-medium">Lecture attendance & hall ticket criteria</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
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

        {/* Handwritten Memo Badge pinned on card */}
        <div className="mb-6 -rotate-1 bg-amber-50/90 border border-amber-200/80 px-3.5 py-1.5 rounded-xl shadow-2xs flex items-center justify-between">
          <span className="font-hand text-sm text-slate-700 font-bold">
            Notice: Minimum 75.0% aggregate required for University Exam Hall Ticket ✍️
          </span>
          <span className="font-mono text-[10px] text-amber-800 font-semibold uppercase">Mandatory</span>
        </div>

        {/* Aggregate Overall Metric Card */}
        <div
          className={`p-5 rounded-2xl mb-6 flex flex-wrap justify-between items-center gap-4 transition-all ${
            isCritical
              ? "bg-gradient-to-r from-rose-50 to-orange-50/60 border border-rose-200 shadow-xs"
              : "bg-gradient-to-r from-emerald-50 to-teal-50/60 border border-emerald-200 shadow-xs"
          }`}
        >
          <div>
            <div className="text-[10px] uppercase font-mono font-bold tracking-wider text-slate-500 flex items-center gap-1.5">
              <BookOpen className="w-3.5 h-3.5" /> AGGREGATE LECTURE ATTENDANCE
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
                ({totalAttended} / {totalConducted} hours attended)
              </span>
            </div>
          </div>

          <div>
            {isCritical ? (
              <span className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold bg-rose-200/90 text-rose-900 border border-rose-300 shadow-xs">
                <AlertTriangle className="w-3.5 h-3.5 text-rose-700" /> Below 75% Criteria
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold bg-emerald-200/90 text-emerald-900 border border-emerald-300 shadow-xs">
                <CheckCircle className="w-3.5 h-3.5 text-emerald-700" /> Good Standing
              </span>
            )}
          </div>
        </div>

        {/* Course-by-Course Attendance Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-slate-200/80 text-slate-400 font-mono text-[10px] uppercase tracking-wider">
              <tr>
                <th className="pb-3 font-bold">Course / Subject</th>
                <th className="pb-3 font-bold text-center">Attended</th>
                <th className="pb-3 font-bold text-right">Ratio</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {records.map((r, idx) => {
                const underQuota = r.percentage < 75.0;
                return (
                  <tr key={idx} className="hover:bg-slate-50/80 transition-colors group">
                    <td className="py-3.5 pr-2">
                      <div className="font-bold text-slate-800 text-xs sm:text-sm group-hover:text-indigo-600 transition-colors">
                        {r.subject_name}
                      </div>
                      {underQuota ? (
                        <span className="font-hand text-xs text-rose-600 font-bold block mt-0.5">
                          Deficit detected • Catch up required ✍️
                        </span>
                      ) : (
                        <span className="font-hand text-xs text-slate-400 block mt-0.5">
                          Criterion satisfied
                        </span>
                      )}
                    </td>
                    <td className="py-3.5 text-center text-xs font-mono font-semibold text-slate-600">
                      {r.total_attended} <span className="text-slate-400">/</span> {r.total_conducted}
                    </td>
                    <td className="py-3.5 text-right">
                      <div className="inline-flex flex-col items-end">
                        <span
                          className={`px-2.5 py-0.5 rounded-lg text-xs font-mono font-extrabold ${
                            underQuota
                              ? "bg-rose-100 text-rose-700 border border-rose-200"
                              : "bg-emerald-100 text-emerald-700 border border-emerald-200"
                          }`}
                        >
                          {r.percentage.toFixed(1)}%
                        </span>
                        {/* Mini progress line */}
                        <div className="w-16 h-1 bg-slate-100 rounded-full mt-1 overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              underQuota ? "bg-rose-500" : "bg-emerald-500"
                            }`}
                            style={{ width: `${Math.min(100, r.percentage)}%` }}
                          />
                        </div>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Footer info & Stale status indicator */}
      {data?.stale && (
        <div className="mt-5 text-xs text-slate-600 bg-slate-100/90 p-3 rounded-xl border border-slate-200 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Clock className="w-3.5 h-3.5 text-indigo-500 flex-shrink-0" />
            <span className="font-medium">Data snapshot verified from encrypted local records.</span>
          </div>
          <span className="font-hand text-sm text-slate-500 hidden sm:inline">Offline-ready ✓</span>
        </div>
      )}
    </div>
  );
};
