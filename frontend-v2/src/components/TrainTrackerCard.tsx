import React, { useEffect, useMemo, useState } from "react";
import {
  ArrowLeftRight,
  Clock,
  Navigation,
  RefreshCw,
  Train,
  Users,
  Activity,
  ChevronRight,
} from "lucide-react";
import { useNextTrains, useTrainStations } from "../hooks/useTrains";
import { useAuthStore } from "../store/useAuthStore";
import type { SuburbanLineCode } from "../types";

// Line branding presets
const LINE_THEMES: Record<SuburbanLineCode, {
  label: string;
  badge: string;
  activeBtn: string;
  accentColor: string;
  borderColor: string;
  dotColor: string;
}> = {
  CR: {
    label: "Central Line",
    badge: "bg-rose-500/15 text-rose-400 border-rose-500/30",
    activeBtn: "bg-rose-600 text-white shadow-lg shadow-rose-900/40 border-rose-500",
    accentColor: "text-rose-400",
    borderColor: "border-rose-500/40",
    dotColor: "bg-rose-500",
  },
  WR: {
    label: "Western Line",
    badge: "bg-sky-500/15 text-sky-400 border-sky-500/30",
    activeBtn: "bg-sky-600 text-white shadow-lg shadow-sky-900/40 border-sky-500",
    accentColor: "text-sky-400",
    borderColor: "border-sky-500/40",
    dotColor: "bg-sky-500",
  },
  HR: {
    label: "Harbour Line",
    badge: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    activeBtn: "bg-emerald-600 text-white shadow-lg shadow-emerald-900/40 border-emerald-500",
    accentColor: "text-emerald-400",
    borderColor: "border-emerald-500/40",
    dotColor: "bg-emerald-500",
  },
  ALL: {
    label: "All Corridors",
    badge: "bg-indigo-500/15 text-indigo-400 border-indigo-500/30",
    activeBtn: "bg-indigo-600 text-white shadow-lg shadow-indigo-900/40 border-indigo-500",
    accentColor: "text-indigo-400",
    borderColor: "border-indigo-500/40",
    dotColor: "bg-indigo-500",
  },
};

// Fallback stations
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

  useEffect(() => {
    if (!isFetching) {
      setSecondsUntilSync(30);
    }
  }, [isFetching]);

  const availableStations = useMemo(() => {
    if (stationsData?.stations && stationsData.stations.length > 0) {
      return stationsData.stations.map((s) => s.name);
    }
    return DEFAULT_STATIONS_BY_LINE[selectedLine] || DEFAULT_STATIONS_BY_LINE.CR;
  }, [stationsData, selectedLine]);

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
    setTimeout(() => setSwapRotating(false), 300);
  };

  const getDepartureCountdown = (depTime: string) => {
    const parts = depTime.split(":").map(Number);
    const now = new Date();
    const trainTime = new Date();
    trainTime.setHours(parts[0], parts[1], parts[2] || 0, 0);

    const diffMs = trainTime.getTime() - now.getTime();
    const diffMins = Math.round(diffMs / 60000);

    if (diffMins <= 0) return { label: "Boarding Now", urgent: true, mins: 0 };
    if (diffMins === 1) return { label: "in 1 min", urgent: true, mins: 1 };
    if (diffMins <= 5) return { label: `in ${diffMins} mins`, urgent: true, mins: diffMins };
    return { label: `in ${diffMins} mins`, urgent: false, mins: diffMins };
  };

  return (
    <div className="glass-panel p-6 sm:p-7 flex flex-col justify-between relative overflow-hidden">
      <div>
        {/* Card Header & Auto-sync badge */}
        <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-sky-900/30">
              <Train className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-white tracking-tight font-heading">
                  Mumbai Suburban Radar
                </h2>
                <span className="inline-flex items-center gap-1 text-[11px] font-mono font-semibold px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                  Live Sync
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Central · Western · Harbour Lines Timetable
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5 text-xs text-slate-400 font-mono bg-slate-800/80 px-3 py-1.5 rounded-lg border border-white/10">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              <span>{secondsUntilSync}s</span>
            </div>
            <button
              onClick={() => refetch()}
              disabled={isFetching}
              title="Refresh Timetable"
              className="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 hover:text-white border border-white/10 transition-all disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? "animate-spin text-sky-400" : ""}`} />
            </button>
          </div>
        </div>

        {/* Corridor Line Switcher Tabs */}
        <div className="mb-4">
          <div className="text-[11px] font-mono font-semibold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
            <Navigation className="w-3 h-3 text-cyan-400" /> Suburban Corridors
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {(["ALL", "CR", "WR", "HR"] as SuburbanLineCode[]).map((lineKey) => {
              const theme = LINE_THEMES[lineKey];
              const isActive = selectedLine === lineKey;
              return (
                <button
                  key={lineKey}
                  type="button"
                  onClick={() => handleLineChange(lineKey)}
                  className={`py-2 px-3 rounded-xl text-xs font-semibold transition-all flex items-center justify-center gap-2 border ${
                    isActive
                      ? theme.activeBtn
                      : "bg-slate-900/60 text-slate-400 border-white/5 hover:border-white/20 hover:text-white"
                  }`}
                >
                  <span className={`w-2 h-2 rounded-full ${theme.dotColor}`} />
                  {lineKey === "ALL" ? "All Corridors" : theme.label.replace(" Line", ` (${lineKey})`)}
                </button>
              );
            })}
          </div>
        </div>

        {/* Station Selectors with Direction Swap */}
        <div className="bg-slate-900/70 rounded-2xl p-4 border border-white/10 mb-5">
          <div className="flex flex-col sm:flex-row items-center gap-3">
            {/* From Station */}
            <div className="w-full sm:flex-1">
              <label className="block text-[11px] font-mono font-medium uppercase tracking-wider text-slate-400 mb-1.5">
                From Station
              </label>
              <select
                value={fromStation}
                onChange={(e) => setRoute(e.target.value, toStation)}
                className="w-full bg-slate-950/80 border border-white/10 font-semibold text-slate-200 text-sm rounded-xl p-2.5 shadow-sm focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 outline-none transition-all cursor-pointer"
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
                className={`p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-cyan-400 border border-white/10 shadow-sm transition-transform duration-300 active:scale-95 ${
                  swapRotating ? "rotate-180" : ""
                }`}
              >
                <ArrowLeftRight className="w-4 h-4" />
              </button>
            </div>

            {/* To Station */}
            <div className="w-full sm:flex-1">
              <label className="block text-[11px] font-mono font-medium uppercase tracking-wider text-slate-400 mb-1.5">
                To Station
              </label>
              <select
                value={toStation}
                onChange={(e) => setRoute(fromStation, e.target.value)}
                className="w-full bg-slate-950/80 border border-white/10 font-semibold text-slate-200 text-sm rounded-xl p-2.5 shadow-sm focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 outline-none transition-all cursor-pointer"
              >
                {availableStations.map((stn) => (
                  <option key={`to-${stn}`} value={stn}>
                    {stn}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Quick Train Type Filter */}
          <div className="flex items-center justify-between mt-3 pt-3 border-t border-white/5 text-xs">
            <span className="text-slate-400 font-mono text-[11px]">Train Type:</span>
            <div className="flex items-center gap-1.5">
              {["ALL", "FAST", "SLOW", "AC FAST"].map((t) => (
                <button
                  key={t}
                  onClick={() => setTrainTypeFilter(t)}
                  className={`px-2 py-0.5 rounded text-[11px] font-mono font-semibold transition-all ${
                    trainTypeFilter === t
                      ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Train List / Schedule Results */}
        <div>
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400 mb-3 uppercase tracking-wider font-mono">
            <span className="flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-cyan-400" /> Next Departing Services
            </span>
            <span>{data?.trains?.length || 0} Trains Found</span>
          </div>

          {isLoading ? (
            <div className="space-y-2.5">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-20 bg-slate-900/50 rounded-2xl animate-pulse border border-white/5" />
              ))}
            </div>
          ) : isError ? (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-center">
              <p className="text-xs text-rose-300">Unable to query train schedules for selected route.</p>
              <button
                onClick={() => refetch()}
                className="mt-2 text-xs text-cyan-400 underline font-mono"
              >
                Retry Query
              </button>
            </div>
          ) : !data?.trains || data.trains.length === 0 ? (
            <div className="p-6 rounded-2xl bg-slate-900/40 border border-white/5 text-center text-slate-400">
              <Train className="w-8 h-8 text-slate-600 mx-auto mb-2" />
              <p className="text-xs">No trains scheduled currently for {fromStation} → {toStation}.</p>
            </div>
          ) : (
            <div className="space-y-2.5 max-h-[380px] overflow-y-auto pr-1">
              {data.trains.map((train, idx) => {
                const countdown = getDepartureCountdown(train.departure_from_source);
                const isFast = train.train_type.includes("FAST");
                const isAC = train.train_type.includes("AC");

                return (
                  <div
                    key={`${train.train_number}-${idx}`}
                    className="p-3.5 rounded-2xl bg-slate-900/60 hover:bg-slate-850/90 border border-white/5 hover:border-cyan-500/30 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3 group"
                  >
                    {/* Left: Timing & Route */}
                    <div className="flex items-center gap-3.5">
                      <div className="text-center min-w-[56px]">
                        <div className="text-base font-bold font-mono text-white">
                          {train.departure_from_source.slice(0, 5)}
                        </div>
                        <div className="text-[10px] font-mono text-slate-400">
                          arr {train.arrival_at_destination.slice(0, 5)}
                        </div>
                      </div>

                      <div className="w-[1px] h-9 bg-white/10" />

                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold font-heading text-slate-200">
                            #{train.train_number}
                          </span>
                          <span
                            className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded ${
                              isAC
                                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                                : isFast
                                ? "bg-rose-500/15 text-rose-300 border border-rose-500/30"
                                : "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30"
                            }`}
                          >
                            {train.train_type}
                          </span>
                          <span className="text-[10px] font-mono text-slate-400 px-1.5 py-0.5 rounded bg-slate-800/80">
                            {train.platform}
                          </span>
                        </div>
                        <div className="text-[11px] text-slate-400 mt-0.5 flex items-center gap-1">
                          <span>{train.source_terminal}</span>
                          <ChevronRight className="w-3 h-3 text-slate-600" />
                          <span>{train.dest_terminal}</span>
                          <span className="text-slate-500">· {train.travel_time_minutes} min</span>
                        </div>
                      </div>
                    </div>

                    {/* Right: Countdown & Crowd Gauge */}
                    <div className="flex items-center justify-between sm:justify-end gap-3 pt-2 sm:pt-0 border-t sm:border-t-0 border-white/5">
                      <div className="text-left sm:text-right">
                        <div className="flex items-center gap-1.5 sm:justify-end">
                          <Users className="w-3 h-3 text-slate-400" />
                          <span
                            className={`text-[11px] font-mono font-semibold ${
                              train.crowd_level === "Heavy Rush"
                                ? "text-rose-400"
                                : train.crowd_level === "Moderate"
                                ? "text-amber-400"
                                : "text-emerald-400"
                            }`}
                          >
                            {train.crowd_level}
                          </span>
                        </div>
                      </div>

                      <div
                        className={`px-3 py-1.5 rounded-xl text-xs font-mono font-bold whitespace-nowrap border ${
                          countdown.urgent
                            ? "bg-rose-500/20 text-rose-300 border-rose-500/40 animate-pulse"
                            : "bg-cyan-500/10 text-cyan-300 border-cyan-500/30"
                        }`}
                      >
                        {countdown.label}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
