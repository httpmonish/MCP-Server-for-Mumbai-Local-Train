import React, { useState } from 'react';

interface AttendanceSummary {
  percentage: number;
  min_percentage_required: number;
  status: 'ABOVE_THRESHOLD' | 'NEAR_THRESHOLD' | 'BELOW_THRESHOLD';
  total_sessions: number;
  counted_sessions: number;
  present_count: number;
  absent_count: number;
  shortage_percentage: number;
  sessions_needed_to_recover: number;
}

interface AttendanceRadarProps {
  summary?: AttendanceSummary;
  onDispatchDelayToken?: () => void;
}

export const AttendanceRadar: React.FC<AttendanceRadarProps> = ({
  summary = {
    percentage: 74.3,
    min_percentage_required: 75.0,
    status: 'BELOW_THRESHOLD',
    total_sessions: 35,
    counted_sessions: 35,
    present_count: 26,
    absent_count: 9,
    shortage_percentage: 0.7,
    sessions_needed_to_recover: 1,
  },
  onDispatchDelayToken,
}) => {
  const [selectedProtocol, setSelectedProtocol] = useState<'A' | 'B'>('A');
  const [dispatched, setDispatched] = useState(false);

  // Circumference for r=42 is 2 * PI * 42 ~= 263.89
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (summary.percentage / 100) * circumference;

  const isCritical = summary.percentage < summary.min_percentage_required;

  const handleDispatch = () => {
    setDispatched(true);
    if (onDispatchDelayToken) onDispatchDelayToken();
    setTimeout(() => setDispatched(false), 3500);
  };

  return (
    <article className="w-full rounded-3xl bg-white/[0.03] backdrop-blur-2xl border border-glass-border p-4 sm:p-6 shadow-xl flex flex-col gap-4 relative overflow-hidden">
      {/* Warning Glow Backdrop */}
      {isCritical && (
        <div className="absolute -right-10 -bottom-10 w-44 h-44 rounded-full bg-signal-rose-glow blur-3xl pointer-events-none"></div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex flex-col">
          <span className="font-mono text-[10px] uppercase text-tertiary tracking-wider flex items-center gap-1 font-semibold">
            <span className="w-2 h-2 rounded-full bg-tertiary"></span>
            VJTI Academic Biometrics
          </span>
          <span className="font-headline text-2xl text-text-primary">Attendance Radar</span>
        </div>
        <span
          className={`font-mono text-[11px] px-2.5 py-1 rounded-full font-medium ${
            isCritical ? 'bg-tertiary/10 text-tertiary border border-tertiary/20' : 'bg-primary/10 text-primary'
          }`}
        >
          {isCritical ? 'Critical' : 'Normal'}
        </span>
      </div>

      {/* Circular Metric Gauge */}
      <div className="flex items-center gap-4 py-1">
        <div className="relative w-28 h-28 shrink-0 flex items-center justify-center">
          <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
            <circle
              cx="50"
              cy="50"
              r={radius}
              fill="none"
              stroke="#1f2022"
              strokeWidth="7"
            />
            <circle
              cx="50"
              cy="50"
              r={radius}
              fill="none"
              stroke={isCritical ? '#ffb2b7' : '#4edea3'}
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              strokeLinecap="round"
              strokeWidth="7"
              className="transition-all duration-1000 ease-out"
            />
          </svg>
          <div className="absolute flex flex-col items-center justify-center">
            <span className="font-headline text-2xl text-text-primary font-normal leading-none">
              {summary.percentage.toFixed(1)}
              <span className="text-sm text-tertiary">%</span>
            </span>
            <span className="font-mono text-[9px] text-text-muted mt-0.5">Overall</span>
          </div>
        </div>

        <div className="flex flex-col gap-1">
          <div className="flex items-baseline gap-1">
            <span className="font-mono text-[11px] text-text-muted">Statutory Threshold:</span>
            <span className="font-mono text-[11px] text-text-primary font-semibold">
              {summary.min_percentage_required.toFixed(1)}%
            </span>
          </div>
          <span className="font-headline-italic italic text-sm text-text-primary leading-snug">
            “1 unexcused absence in CS-602 DBMS triggers semester examination debarment.”
          </span>
          <span className="font-mono text-[10px] text-text-muted">
            Biometric Machine #04 Closes: 09:30 AM Sharp
          </span>
        </div>
      </div>

      {/* Dynamic Contingency Protocol Selectors */}
      <div className="flex flex-col gap-2 pt-1">
        <span className="font-mono text-[10px] uppercase text-text-muted tracking-wider">
          Contingency Protocols
        </span>

        {/* Protocol A */}
        <div
          onClick={() => setSelectedProtocol('A')}
          className={`p-3 rounded-2xl cursor-pointer transition-all flex flex-col gap-1.5 border ${
            selectedProtocol === 'A'
              ? 'bg-white/[0.08] border-primary/40 shadow-lg shadow-primary/5'
              : 'bg-white/[0.02] border-glass-border hover:bg-white/[0.05]'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="font-body text-xs text-text-primary font-medium flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-primary"></span>
              Sprint: Board 08:47 FAST
            </span>
            <span className="font-mono text-xs text-primary">ETA 09:23 AM</span>
          </div>
          <p className="font-body text-[11px] text-text-secondary leading-normal">
            Arrives Matunga Platform 1. 7 min brisk walk to Mechanical Building. Safe for 09:30 biometric timestamp.
          </p>
        </div>

        {/* Protocol B */}
        <div
          onClick={() => setSelectedProtocol('B')}
          className={`p-3 rounded-2xl cursor-pointer transition-all flex flex-col gap-1.5 border ${
            selectedProtocol === 'B'
              ? 'bg-white/[0.08] border-secondary/40 shadow-lg shadow-secondary/5'
              : 'bg-white/[0.02] border-glass-border hover:bg-white/[0.05]'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="font-body text-xs text-text-primary font-medium flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-secondary"></span>
              Generate Official CR Delay Slip
            </span>
            <span className="font-mono text-xs text-secondary">Token Verified</span>
          </div>
          <p className="font-body text-[11px] text-text-secondary leading-normal">
            Dispatches signed Suburban Transit Telemetry Certificate to Prof. K. Mehta (HOD Dept. CS) with GPS proof.
          </p>
        </div>
      </div>

      {/* Quick Action Button */}
      <button
        onClick={handleDispatch}
        className={`w-full py-2.5 rounded-full font-body text-xs font-semibold transition-all flex items-center justify-center gap-2 cursor-pointer border ${
          dispatched
            ? 'bg-primary/20 text-primary border-primary/40'
            : 'bg-white/[0.06] hover:bg-white/[0.12] text-text-primary border-glass-border'
        }`}
      >
        <span className="material-symbols-outlined text-[18px]">
          {dispatched ? 'check_circle' : 'verified_user'}
        </span>
        <span>{dispatched ? 'Token Dispatched to HOD CS' : 'Issue Signed Delay Token'}</span>
      </button>
    </article>
  );
};
