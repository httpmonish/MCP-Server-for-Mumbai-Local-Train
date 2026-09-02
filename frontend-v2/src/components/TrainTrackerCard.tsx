import React from "react";
import { useNextTrains } from "../hooks/useTrains";
import { useAuthStore } from "../store/useAuthStore";
import { ArrowLeftRight, Train, Zap } from "lucide-react";

const STATIONS = ["CSMT", "Byculla", "Dadar", "Kurla", "Ghatkopar", "Thane", "Dombivli", "Kalyan"];

export const TrainTrackerCard: React.FC = () => {
  const { fromStation, toStation, setRoute, swapRoute } = useAuthStore();
  const { data, isLoading, isError, refetch } = useNextTrains();

  const getRelativeMinutes = (timeStr: string) => {
    const [h, m] = timeStr.split(":").map(Number);
    const now = new Date();
    const trainTime = new Date();
    trainTime.setHours(h, m, 0, 0);

    const diffMs = trainTime.getTime() - now.getTime();
    const diffMins = Math.round(diffMs / 60000);
    return diffMins > 0 ? `in ${diffMins} min${diffMins === 1 ? "" : "s"}` : "Departing now";
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col justify-between">
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
            <Train className="w-5 h-5 text-indigo-600"/> Commute Tracker
          </h2>
          <span className="text-xs bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-full font-medium">
            30s Auto-Sync
          </span>
        </div>

        {/* Station Selectors */}
        <div className="flex items-center gap-2 mb-6">
          <select
            value={fromStation}
            onChange={(e) => setRoute(e.target.value, toStation)}
            className="w-full bg-slate-50 border border-slate-200 text-slate-700 text-sm rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 outline-none"
          >
            {STATIONS.map((stn) => (
              <option key={stn} value={stn}>{stn}</option>
            ))}
          </select>

          <button
            onClick={swapRoute}
            title="Swap Stations"
            className="p-2.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-600 transition-colors"
          >
            <ArrowLeftRight className="w-4 h-4"/>
          </button>

          <select
            value={toStation}
            onChange={(e) => setRoute(fromStation, e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 text-slate-700 text-sm rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 outline-none"
          >
            {STATIONS.map((stn) => (
              <option key={stn} value={stn}>{stn}</option>
            ))}
          </select>
        </div>

        {/* Train List */}
        {isLoading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((n) => (
              <div key={n} className="h-16 bg-slate-100 rounded-lg animate-pulse"></div>
            ))}
          </div>
        ) : isError ? (
          <div className="text-center py-6 text-sm text-rose-600">
            Failed to query schedules.
            <button onClick={() => refetch()} className="block mx-auto mt-2 underline font-medium">Retry</button>
          </div>
        ) : data?.trains.length === 0 ? (
          <div className="text-center py-8 text-slate-400 text-sm">
            No upcoming trains found for this route right now.
          </div>
        ) : (
          <div className="space-y-3">
            {data?.trains.map((train, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-lg border border-slate-100 bg-slate-50/50 hover:bg-slate-50 flex items-center justify-between transition-colors"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-800 text-sm">#{train.train_number}</span>
                    <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${train.train_type === "FAST" ? "bg-purple-100 text-purple-700" : "bg-blue-100 text-blue-700"}`}>
                      {train.train_type === "FAST" && <Zap className="w-3 h-3 inline mr-0.5"/>}
                      {train.train_type}
                    </span>
                    <span className="text-[10px] bg-slate-200 text-slate-700 px-1.5 py-0.5 rounded font-bold">
                      {train.line}
                    </span>
                  </div>
                  <div className="text-xs text-slate-500 mt-1">
                    Departs {train.departure_from_source} → Arrives {train.arrival_at_destination} ({train.travel_time_minutes}m)
                  </div>
                </div>
                <div className="text-right">
                  <span className="inline-block bg-indigo-50 text-indigo-700 border border-indigo-200 text-xs font-bold px-2.5 py-1 rounded-md">
                    {getRelativeMinutes(train.departure_from_source)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
