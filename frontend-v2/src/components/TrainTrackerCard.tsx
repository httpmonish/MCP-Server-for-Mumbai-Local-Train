import React, { useEffect, useMemo, useState } from "react";
import {
  ArrowLeftRight,
  Clock,
  Filter,
  Navigation,
  RefreshCw,
  Sparkles,
  Train,
  Users,
  Zap,
} from "lucide-react";
import { useNextTrains, useTrainStations } from "../hooks/useTrains";
import { useAuthStore } from "../store/useAuthStore";
import type { SuburbanLineCode } from "../types";

// Line branding presets
const LINE_THEMES: Record<SuburbanLineCode, {
  label: string;
  badge: string;
  activeBtn: string;
  borderColor: string;
  bgGlow: string;
  tagColor: string;
}> = {
  CR: {
    label: "Central Line",
    badge: "bg-rose-500/15 text-rose-600 border-rose-200 dark:border-rose-900/50",
    activeBtn: "bg-rose-600 text-white shadow-rose-200 shadow-lg",
    borderColor: "border-rose-500",
    bgGlow: "from-rose-500/10 via-transparent to-transparent",
    tagColor: "bg-rose-600 text-white",
  },
  WR: {
    label: "Western Line",
    badge: "bg-blue-500/15 text-blue-600 border-blue-200 dark:border-blue-900/50",
    activeBtn: "bg-blue-600 text-white shadow-blue-200 shadow-lg",
    borderColor: "border-blue-500",
    bgGlow: "from-blue-500/10 via-transparent to-transparent",
    tagColor: "bg-blue-600 text-white",
  },
  HR: {
    label: "Harbour Line",
    badge: "bg-emerald-500/15 text-emerald-600 border-emerald-200 dark:border-emerald-900/50",
    activeBtn: "bg-emerald-600 text-white shadow-emerald-200 shadow-lg",
    borderColor: "border-emerald-500",
    bgGlow: "from-emerald-500/10 via-transparent to-transparent",
    tagColor: "bg-emerald-600 text-white",
  },
  ALL: {
    label: "All Corridors",
    badge: "bg-indigo-500/15 text-indigo-600 border-indigo-200 dark:border-indigo-900/50",
    activeBtn: "bg-indigo-600 text-white shadow-indigo-200 shadow-lg",
    borderColor: "border-indigo-500",
    bgGlow: "from-indigo-500/10 via-transparent to-transparent",
    tagColor: "bg-slate-800 text-white",
  },
};

// Fallback stations if API is warming up
const DEFAULT_STATIONS_BY_LINE: Record<SuburbanLineCode, string[]> = {
  CR: ["CSMT", "Byculla", "Dadar", "Kurla", "Ghatkopar", "Thane", "Dombivli", "Kalyan", "Titwala", "Kasara"],
  WR: ["Churchgate", "Mumbai Central", "Dadar", "Bandra", "Andheri", "Borivali", "Bhayandar", "Virar"],
  HR: ["CSMT", "Sandhurst Road", "Vadala Road", "Kurla", "Vashi", "Nerul", "Belapur", "Panvel"],
  ALL: ["CSMT", "Churchgate", "Dadar", "Bandra", "Kurla", "Andheri", "Thane", "Borivali", "Kalyan", "Kasara", "Panvel"],
};

export const TrainTrackerCard: React.FC = () => {
  const {
    fromStation,
    toStation,
    selectedLine,
    trainTypeFilter,
    setRoute,
    swapRoute,
    setSelectedLine,
    setTrainTypeFilter,
  } = useAuthStore();

  const [swapRotating, setSwapRotating] = useState(false);
  const [secondsUntilSync, setSecondsUntilSync] = useState(30);

  const { data: stationsData } = useTrainStations(selectedLine === "ALL" ? undefined : selectedLine);
  const { data, isLoading, isError, refetch, isFetching } = useNextTrains();

  // Dynamic countdown timer for the next poll
  useEffect(() => {
    const timer = setInterval(() => {
      setSecondsUntilSync((prev) => (prev <= 1 ? 30 : prev - 1));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // When fetch completes, reset countdown
  useEffect(() => {
    if (!isFetching) {
      setSecondsUntilSync(30);
    }
  }, [isFetching]);

  // Compute available station names based on selected line
  const availableStations = useMemo(() => {
    if (stationsData?.stations && stationsData.stations.length > 0) {
      return stationsData.stations.map((s) => s.name);
    }
    return DEFAULT_STATIONS_BY_LINE[selectedLine] || DEFAULT_STATIONS_BY_LINE.CR;
  }, [stationsData, selectedLine]);

  // Handle line tab change and adjust default stations if current ones aren't on that line
  const handleLineChange = (newLine: SuburbanLineCode) => {
    setSelectedLine(newLine);
    if (newLine === "WR") {
      setRoute("Churchgate", "Borivali");
    } else if (newLine === "HR") {
      setRoute("CSMT", "Panvel");
    } else if (newLine === "CR") {
      setRoute("CSMT", "Thane");
    }
  };


  const handleSwap = () => {
    setSwapRotating(true);
    swapRoute();
    setTimeout(() => setSwapRotating(false), 350);
  };

  const getDepartureCountdown = (depTime: string) => {
    const parts = depTime.split(":").map(Number);
    const now = new Date();
    const trainTime = new Date();
    trainTime.setHours(parts[0], parts[1], parts[2] || 0, 0);

    const diffMs = trainTime.getTime() - now.getTime();
    const diffMins = Math.round(diffMs / 60000);

    if (diffMins <= 0) return { label: "Boarding / Dep.", urgent: true, mins: 0 };
    if (diffMins === 1) return { label: "in 1 min", urgent: true, mins: 1 };
    if (diffMins <= 5) return { label: `in ${diffMins} mins`, urgent: true, mins: diffMins };
    return { label: `in ${diffMins} mins`, urgent: false, mins: diffMins };
  };

  const currentTheme = LINE_THEMES[selectedLine] || LINE_THEMES.ALL;

  return (
    <div className={`relative overflow-hidden bg-white/95 backdrop-blur-md rounded-2xl shadow-xl border border-slate-200/80 p-6 flex flex-col justify-between transition-all duration-300`}>
      {/* Subtle top ambient glow based on active line */}
      <div className={`absolute -top-24 -right-24 w-72 h-72 rounded-full bg-gradient-to-br ${currentTheme.bgGlow} blur-3xl pointer-events-none`} />

      <div>
        {/* Card Header & Auto-sync badge */}
        <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-slate-900 to-indigo-700 flex items-center justify-center text-white shadow-md">
              <Train className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-black text-slate-900 tracking-tight">Mumbai Local Live</h2>
                <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping" />
                  Live Sync
                </span>
              </div>
              <p className="text-xs text-slate-500 font-medium">Real-time suburban timetables across corridors</p>
            </div>
          </div>

          {/* Sync status & Refresh button */}
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5 text-xs text-slate-500 font-semibold bg-slate-100/90 px-3 py-1.5 rounded-lg border border-slate-200">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              <span>{secondsUntilSync}s</span>
            </div>
            <button
              onClick={() => refetch()}
              disabled={isFetching}
              title="Refresh Timetable"
              className="p-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 hover:text-slate-900 transition-all border border-slate-200 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${isFetching ? "animate-spin text-indigo-600" : ""}`} />
            </button>
          </div>
        </div>

        {/* Corridor Line Switcher Tabs */}
        <div className="mb-5">
          <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-1.5">
            <Navigation className="w-3 h-3 text-indigo-500" /> Select Suburban Corridor
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <button
              type="button"
              onClick={() => handleLineChange("ALL")}
              className={`py-2 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 border ${
                selectedLine === "ALL"
                  ? "bg-slate-900 text-white border-slate-900 shadow-md scale-[1.02]"
                  : "bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100"
              }`}
            >
              <Sparkles className="w-3.5 h-3.5" /> All Lines
            </button>

            <button
              type="button"
              onClick={() => handleLineChange("CR")}
              className={`py-2 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 border ${
                selectedLine === "CR"
                  ? "bg-rose-600 text-white border-rose-600 shadow-md shadow-rose-200 scale-[1.02]"
                  : "bg-rose-50/60 text-rose-700 border-rose-200/80 hover:bg-rose-100"
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-rose-500 inline-block" />
              Central (CR)
            </button>

            <button
              type="button"
              onClick={() => handleLineChange("WR")}
              className={`py-2 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 border ${
                selectedLine === "WR"
                  ? "bg-blue-600 text-white border-blue-600 shadow-md shadow-blue-200 scale-[1.02]"
                  : "bg-blue-50/60 text-blue-700 border-blue-200/80 hover:bg-blue-100"
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-blue-500 inline-block" />
              Western (WR)
            </button>

            <button
              type="button"
              onClick={() => handleLineChange("HR")}
              className={`py-2 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 border ${
                selectedLine === "HR"
                  ? "bg-emerald-600 text-white border-emerald-600 shadow-md shadow-emerald-200 scale-[1.02]"
                  : "bg-emerald-50/60 text-emerald-700 border-emerald-200/80 hover:bg-emerald-100"
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" />
              Harbour (HR)
            </button>
          </div>
        </div>

        {/* Station Selectors with Direction Swap */}
        <div className="bg-slate-50/90 rounded-xl p-3.5 border border-slate-200 mb-4">
          <div className="flex flex-col sm:flex-row items-center gap-2.5">
            {/* From Station */}
            <div className="w-full sm:flex-1">
              <label className="block text-[10px] font-extrabold uppercase tracking-wider text-slate-500 mb-1">
                From Station
              </label>
              <select
                value={fromStation}
                onChange={(e) => setRoute(e.target.value, toStation)}
                className="w-full bg-white border border-slate-300 font-semibold text-slate-800 text-sm rounded-lg p-2.5 shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all cursor-pointer"
              >
                {availableStations.map((stn) => (
                  <option key={`from-${stn}`} value={stn}>
                    {stn}
                  </option>
                ))}
              </select>
            </div>

            {/* Swap Button */}
            <div className="sm:pt-5">
              <button
                type="button"
                onClick={handleSwap}
                title="Swap Direction"
                className={`p-2.5 rounded-full bg-white border border-slate-300 hover:border-indigo-400 hover:bg-indigo-50 text-slate-700 shadow-sm transition-transform duration-300 active:scale-95 ${
                  swapRotating ? "rotate-180" : ""
                }`}
              >
                <ArrowLeftRight className="w-4 h-4 text-indigo-600" />
              </button>
            </div>

            {/* To Station */}
            <div className="w-full sm:flex-1">
              <label className="block text-[10px] font-extrabold uppercase tracking-wider text-slate-500 mb-1">
                To Station
              </label>
              <select
                value={toStation}
                onChange={(e) => setRoute(fromStation, e.target.value)}
                className="w-full bg-white border border-slate-300 font-semibold text-slate-800 text-sm rounded-lg p-2.5 shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all cursor-pointer"
              >
                {availableStations.map((stn) => (
                  <option key={`to-${stn}`} value={stn}>
                    {stn}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Quick Station Suggestions */}
          <div className="mt-3 pt-2.5 border-t border-slate-200/80 flex flex-wrap items-center gap-1.5 text-xs">
            <span className="text-[10px] font-bold text-slate-500 uppercase">Popular Hubs:</span>
            {["CSMT", "Dadar", "Kurla", "Andheri", "Thane", "Borivali"].map((hub) => (
              <button
                key={hub}
                type="button"
                onClick={() => {
                  if (fromStation !== hub) setRoute(fromStation, hub);
                  else setRoute("CSMT", hub);
                }}
                className="px-2 py-0.5 rounded text-[11px] font-medium bg-white hover:bg-indigo-50 border border-slate-200 hover:border-indigo-300 text-slate-700 transition-colors"
              >
                {hub}
              </button>
            ))}
          </div>
        </div>

        {/* Speed / AC Train Type Filter Chips */}
        <div className="flex items-center justify-between gap-2 mb-4">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 font-bold uppercase tracking-wider">
            <Filter className="w-3.5 h-3.5 text-indigo-500" /> Filter:
          </div>
          <div className="flex items-center gap-1.5">
            {[
              { id: "ALL", label: "All Types" },
              { id: "FAST", label: "⚡ Fast", color: "text-purple-700 bg-purple-50 border-purple-200" },
              { id: "SLOW", label: "🐢 Slow", color: "text-blue-700 bg-blue-50 border-blue-200" },
              { id: "AC", label: "❄️ AC Local", color: "text-cyan-700 bg-cyan-50 border-cyan-200" },
            ].map((f) => (
              <button
                key={f.id}
                type="button"
                onClick={() => setTrainTypeFilter(f.id)}
                className={`text-xs px-2.5 py-1 rounded-lg font-bold transition-all border ${
                  trainTypeFilter === f.id
                    ? "bg-slate-900 text-white border-slate-900 shadow-sm"
                    : "bg-white text-slate-600 border-slate-200 hover:bg-slate-50"
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>

        {/* Train List Display */}
        {isLoading ? (
          <div className="space-y-3">
            {[1, 2, 3, 4].map((n) => (
              <div key={n} className="h-20 bg-slate-100/80 rounded-xl animate-pulse flex items-center p-4">
                <div className="w-12 h-12 bg-slate-200 rounded-lg mr-3" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-slate-200 rounded w-1/3" />
                  <div className="h-3 bg-slate-200 rounded w-1/2" />
                </div>
              </div>
            ))}
          </div>
        ) : isError ? (
          <div className="text-center py-10 px-4 rounded-xl border border-dashed border-rose-300 bg-rose-50/50">
            <p className="text-sm font-semibold text-rose-700 mb-2">Unable to retrieve timetable data</p>
            <p className="text-xs text-rose-500 mb-4">Check if destination is further along the selected corridor</p>
            <button
              onClick={() => refetch()}
              className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-xs font-bold transition-colors shadow-sm"
            >
              Retry Query
            </button>
          </div>
        ) : data?.trains.length === 0 ? (
          <div className="text-center py-10 px-4 rounded-xl border border-dashed border-slate-300 bg-slate-50">
            <Train className="w-8 h-8 text-slate-300 mx-auto mb-2" />
            <p className="text-sm font-bold text-slate-700 mb-1">No upcoming trains found for this route</p>
            <p className="text-xs text-slate-500 max-w-sm mx-auto mb-3">
              Ensure <span className="font-semibold text-slate-700">{fromStation}</span> comes before{" "}
              <span className="font-semibold text-slate-700">{toStation}</span> in travel direction, or click swap.
            </p>
            <button
              onClick={handleSwap}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-bold transition-colors shadow-sm"
            >
              <ArrowLeftRight className="w-3.5 h-3.5" /> Swap Direction
            </button>
          </div>
        ) : (
          <div className="space-y-3 max-h-[460px] overflow-y-auto pr-1">
            {data?.trains.map((train, idx) => {
              const countdown = getDepartureCountdown(train.departure_from_source);
              const isFast = train.train_type.includes("FAST");
              const isAC = train.train_type.includes("AC");

              const lineBadgeColor =
                train.line === "WR"
                  ? "bg-blue-600 text-white"
                  : train.line === "HR"
                  ? "bg-emerald-600 text-white"
                  : "bg-rose-600 text-white";

              return (
                <div
                  key={`${train.train_number}-${idx}`}
                  className="group relative p-4 rounded-xl border border-slate-200/90 bg-white hover:border-indigo-300 hover:shadow-md transition-all duration-200"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      {/* Train Number, Line Tag & Speed Badge */}
                      <div className="flex flex-wrap items-center gap-2 mb-1.5">
                        <span className={`text-[10px] font-black px-2 py-0.5 rounded shadow-sm ${lineBadgeColor}`}>
                          {train.line_name || `${train.line} LINE`}
                        </span>

                        <span className="font-extrabold text-slate-900 text-sm tracking-tight">
                          #{train.train_number}
                        </span>

                        {/* Train Type Badges */}
                        <span
                          className={`text-[10px] font-black px-2 py-0.5 rounded-full flex items-center gap-0.5 border ${
                            isAC
                              ? "bg-cyan-100 text-cyan-800 border-cyan-300"
                              : isFast
                              ? "bg-purple-100 text-purple-800 border-purple-300"
                              : "bg-slate-100 text-slate-700 border-slate-200"
                          }`}
                        >
                          {isFast && <Zap className="w-3 h-3 text-purple-600 fill-purple-600" />}
                          {train.train_type}
                        </span>

                        {/* Platform Badge */}
                        {train.platform && (
                          <span className="text-[10px] font-extrabold px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200">
                            {train.platform}
                          </span>
                        )}
                      </div>

                      {/* Station Hops & Time */}
                      <div className="flex items-center gap-2 text-xs font-medium text-slate-700 mt-1">
                        <span className="font-bold text-slate-900">{train.departure_from_source.substring(0, 5)}</span>
                        <span className="text-slate-400">→</span>
                        <span className="font-bold text-slate-900">{train.arrival_at_destination.substring(0, 5)}</span>
                        <span className="text-slate-400">|</span>
                        <span className="text-slate-500 font-semibold">{train.travel_time_minutes} mins ride</span>
                      </div>

                      {/* Route Bound Info */}
                      {train.dest_terminal && (
                        <div className="text-[11px] text-slate-500 mt-1 flex items-center gap-1">
                          <span>Bound for</span>
                          <span className="font-bold text-slate-700">{train.dest_terminal}</span>
                        </div>
                      )}
                    </div>

                    {/* Right side: Departure countdown & crowd indicator */}
                    <div className="text-right flex flex-col items-end gap-1.5">
                      <div
                        className={`inline-flex items-center gap-1 text-xs font-black px-3 py-1.5 rounded-lg border shadow-sm ${
                          countdown.urgent
                            ? "bg-rose-50 text-rose-700 border-rose-200 animate-pulse"
                            : "bg-indigo-50 text-indigo-700 border-indigo-200"
                        }`}
                      >
                        <Clock className="w-3.5 h-3.5" />
                        {countdown.label}
                      </div>

                      {/* Crowd Level Indicator */}
                      {train.crowd_level && (
                        <span
                          className={`text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1 ${
                            train.crowd_level === "Heavy Rush"
                              ? "bg-rose-100 text-rose-800"
                              : train.crowd_level === "Moderate"
                              ? "bg-amber-100 text-amber-800"
                              : "bg-emerald-100 text-emerald-800"
                          }`}
                        >
                          <Users className="w-2.5 h-2.5" />
                          {train.crowd_level}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Network Status Footer */}
      <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500 font-medium">
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-500" />
          Central • Western • Harbour Frequency: Active
        </span>
        <span className="font-semibold text-slate-700">MRVC Timetable Verified</span>
      </div>
    </div>
  );
};
