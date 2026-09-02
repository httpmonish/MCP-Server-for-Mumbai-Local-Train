import React from "react";
import { useAttendance } from "../hooks/useAcademic";
import { AlertTriangle, CheckCircle, Clock } from "lucide-react";

export const AttendanceCard: React.FC = () => {
  const { data, isLoading, isError, error, refetch, isFetching } = useAttendance();

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 animate-pulse">
        <div className="h-6 bg-slate-200 rounded w-1/3 mb-4"></div>
        <div className="h-16 bg-slate-100 rounded mb-4"></div>
        <div className="space-y-3">
          <div className="h-8 bg-slate-100 rounded"></div>
          <div className="h-8 bg-slate-100 rounded"></div>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-rose-200 p-6">
        <h3 className="text-lg font-semibold text-rose-800 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5"/> Attendance Retrieval Failed
        </h3>
        <p className="text-sm text-rose-600 mt-2">{(error as any)?.detail || "Error loading records."}</p>
        <button
          onClick={() => refetch()}
          className="mt-4 px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white text-sm rounded-lg transition-colors"
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
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col justify-between">
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-slate-800">Academic Attendance</h2>
          {isFetching && <Clock className="w-4 h-4 text-slate-400 animate-spin"/>}
        </div>

        <div className={`p-4 rounded-xl mb-6 flex justify-between items-center ${isCritical ? "bg-rose-50 border border-rose-200" : "bg-emerald-50 border border-emerald-200"}`}>
          <div>
            <div className="text-xs uppercase font-bold tracking-wider text-slate-500">Aggregate Overall</div>
            <div className={`text-3xl font-extrabold ${isCritical ? "text-rose-700" : "text-emerald-700"}`}>
              {aggregatePct.toFixed(1)}%
            </div>
          </div>
          <div>
            {isCritical ? (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-rose-200 text-rose-800">
                <AlertTriangle className="w-3.5 h-3.5"/> Below 75% Criteria
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-200 text-emerald-800">
                <CheckCircle className="w-3.5 h-3.5"/> Good Standing
              </span>
            )}
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-slate-100 text-slate-400 text-xs uppercase">
              <tr>
                <th className="pb-3 font-semibold">Subject</th>
                <th className="pb-3 font-semibold text-center">Attended</th>
                <th className="pb-3 font-semibold text-right">Percentage</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {records.map((r, idx) => (
                <tr key={idx} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-3 font-medium text-slate-700">{r.subject_name}</td>
                  <td className="py-3 text-center text-slate-500">{r.total_attended} / {r.total_conducted}</td>
                  <td className="py-3 text-right">
                    <span className={`px-2 py-0.5 rounded text-xs font-bold ${r.percentage < 75 ? "bg-rose-100 text-rose-700" : "bg-emerald-100 text-emerald-700"}`}>
                      {r.percentage.toFixed(1)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {data?.stale && (
        <div className="mt-4 text-xs text-amber-700 bg-amber-50 p-2.5 rounded border border-amber-200 flex items-center gap-1.5">
          <Clock className="w-3.5 h-3.5 flex-shrink-0"/>
          <span>Showing cached database snapshot. Live portal currently unreachable.</span>
        </div>
      )}
    </div>
  );
};
