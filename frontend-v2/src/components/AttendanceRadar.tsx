import React, { useState } from 'react';
import { motion } from 'framer-motion';
import type { AttendanceRiskResult, DelayTokenPayload } from '../lib/services/telemetryService';
import type { PersonaType } from './modals/UserProfilePopover';
import { PedestrianSprintModal } from './modals/PedestrianSprintModal';
import { DelayCertificateModal } from './modals/DelayCertificateModal';

interface AttendanceRadarProps {
  riskData: AttendanceRiskResult;
  tokenData: DelayTokenPayload;
  persona?: PersonaType;
}

export const AttendanceRadar: React.FC<AttendanceRadarProps> = ({
  riskData,
  tokenData,
  persona = 'COMMUTER',
}) => {
  const [selectedProtocol, setSelectedProtocol] = useState<'A' | 'B'>('A');
  const [sprintModalOpen, setSprintModalOpen] = useState(false);
  const [delayModalOpen, setDelayModalOpen] = useState(false);

  // Circumference for r=42 is 2 * PI * 42 ~= 263.89
  const radius = 42;
  const circumference = 2 * Math.PI * radius;

  // Custom percentages based on persona
  const targetPercent =
    persona === 'COMMUTER'
      ? 96.4
      : persona === 'CORPORATE'
      ? 98.2
      : riskData.simulatedPercentage;

  const minRequired = persona === 'STUDENT' ? riskData.minRequiredPercentage : 90.0;
  const offset = circumference - (targetPercent / 100) * circumference;
  const isCritical = persona === 'STUDENT' && targetPercent < minRequired;

  return (
    <article className="w-full rounded-3xl bg-white/[0.03] backdrop-blur-2xl border border-glass-border p-4 sm:p-6 shadow-xl flex flex-col gap-4 relative overflow-hidden">
      {/* Warning Glow Backdrop for Student Critical State */}
      {isCritical && (
        <div className="absolute -right-10 -bottom-10 w-48 h-48 rounded-full bg-signal-rose-glow blur-3xl pointer-events-none animate-pulse"></div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex flex-col">
          <span className="font-mono text-[10px] uppercase text-tertiary tracking-wider flex items-center gap-1 font-semibold">
            <span className="w-2 h-2 rounded-full bg-tertiary"></span>
            {persona === 'STUDENT'
              ? 'VJTI Academic Biometrics'
              : persona === 'CORPORATE'
              ? 'Workplace Commute Telemetry'
              : 'Suburban Commute Telemetry'}
          </span>
          <span className="font-headline text-2xl text-text-primary">
            {persona === 'STUDENT' ? 'Attendance Radar' : 'Punctuality Radar'}
          </span>
        </div>
        <span
          className={`font-mono text-[11px] px-2.5 py-1 rounded-full font-medium ${
            isCritical
              ? 'bg-signal-rose/20 text-signal-rose border border-signal-rose/30 font-bold'
              : 'bg-primary/10 text-primary border border-primary/20 font-bold'
          }`}
        >
          {persona === 'STUDENT'
            ? isCritical
              ? 'Debarment Risk'
              : 'Safe (≥75%)'
            : 'Punctual Flow (96%)'}
        </span>
      </div>

      {/* Circular Dynamic Metric Gauge with Spring Physics */}
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
            <motion.circle
              cx="50"
              cy="50"
              r={radius}
              fill="none"
              stroke={isCritical ? '#ff5c6c' : '#4edea3'}
              strokeDasharray={circumference}
              initial={{ strokeDashoffset: circumference }}
              animate={{ strokeDashoffset: offset }}
              transition={{ type: 'spring', damping: 20, stiffness: 100 }}
              strokeLinecap="round"
              strokeWidth="7"
            />
          </svg>
          <div className="absolute flex flex-col items-center justify-center">
            <span className="font-headline text-2xl text-text-primary font-normal leading-none">
              {targetPercent.toFixed(1)}
              <span className={`text-sm ${isCritical ? 'text-signal-rose' : 'text-primary'}`}>%</span>
            </span>
            <span className="font-mono text-[9px] text-text-muted mt-0.5">
              {persona === 'STUDENT' ? 'Projected' : 'On-Time'}
            </span>
          </div>
        </div>

        <div className="flex flex-col gap-1">
          <div className="flex items-baseline gap-1">
            <span className="font-mono text-[11px] text-text-muted">
              {persona === 'STUDENT' ? 'Statutory Threshold:' : 'Target Reliability:'}
            </span>
            <span className="font-mono text-[11px] text-text-primary font-semibold">
              {persona === 'STUDENT' ? `${minRequired.toFixed(1)}%` : '±5m On-Time'}
            </span>
          </div>
          <span className="font-headline-italic italic text-sm text-text-primary leading-snug">
            {persona === 'STUDENT'
              ? isCritical
                ? '“1 unexcused absence in CS-602 DBMS triggers semester examination debarment.”'
                : '“Commute on track for on-time biometric timestamp in Mechanical Bldg.”'
              : persona === 'CORPORATE'
              ? '“Suburban rakes operating within optimal work-shift arrival window.”'
              : '“Commute buffer verified: +12m arrival window before target schedule.”'}
          </span>
          <span className="font-mono text-[10px] text-text-muted">
            {persona === 'STUDENT'
              ? `Biometric Machine #04 Closes: ${riskData.lectureStartTime} Sharp`
              : `Target Window: ${riskData.lectureStartTime} Arrival`}
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
          onClick={() => {
            setSelectedProtocol('A');
            setSprintModalOpen(true);
          }}
          className={`p-3 rounded-2xl cursor-pointer transition-all flex flex-col gap-1.5 border ${
            selectedProtocol === 'A'
              ? 'bg-white/[0.08] border-primary/40 shadow-lg shadow-primary/5'
              : 'bg-white/[0.02] border-glass-border hover:bg-white/[0.05]'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="font-body text-xs text-text-primary font-medium flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-primary"></span>
              {persona === 'STUDENT'
                ? 'Sprint: Fast Walk from Matunga E.'
                : 'Express Flow: Board Fast Rake'}
            </span>
            <span className="font-mono text-xs text-primary font-bold">
              {persona === 'STUDENT' ? '7m Path ETA' : 'Optimal Path'}
            </span>
          </div>
          <p className="font-body text-[11px] text-text-secondary leading-normal">
            {persona === 'STUDENT'
              ? 'Arrives Matunga Platform 1. 7 min brisk walk to Mechanical Building. Safe for 09:30 biometric timestamp.'
              : 'Direct express route with minimal crossover delay. Arrives destination platform on schedule.'}
          </p>
        </div>

        {/* Protocol B */}
        <div
          onClick={() => {
            setSelectedProtocol('B');
            setDelayModalOpen(true);
          }}
          className={`p-3 rounded-2xl cursor-pointer transition-all flex flex-col gap-1.5 border ${
            selectedProtocol === 'B'
              ? 'bg-white/[0.08] border-secondary/40 shadow-lg shadow-secondary/5'
              : 'bg-white/[0.02] border-glass-border hover:bg-white/[0.05]'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="font-body text-xs text-text-primary font-medium flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-secondary"></span>
              Official CR Delay Certificate
            </span>
            <span className="font-mono text-xs text-secondary font-bold">SHA-256 Signed</span>
          </div>
          <p className="font-body text-[11px] text-text-secondary leading-normal">
            {persona === 'STUDENT'
              ? 'Dispatches signed Suburban Transit Telemetry Certificate to Prof. K. Mehta (HOD Dept. CS) with GPS proof.'
              : 'Generates authenticated Central Railway transit disruption certificate for employer or institutional proof.'}
          </p>
        </div>
      </div>

      {/* Quick Action Button */}
      <button
        onClick={() => setDelayModalOpen(true)}
        className="w-full py-2.5 rounded-full font-body text-xs font-semibold transition-all flex items-center justify-center gap-2 cursor-pointer border bg-white/[0.06] hover:bg-white/[0.12] text-text-primary border-glass-border hover:border-primary/40"
      >
        <span className="material-symbols-outlined text-[18px] text-primary">verified_user</span>
        <span>Issue Signed Delay Token</span>
      </button>

      {/* Sprint Modal */}
      <PedestrianSprintModal
        isOpen={sprintModalOpen}
        onClose={() => setSprintModalOpen(false)}
        trainArrivalTime={riskData.etaDadar}
        lectureStartTime={riskData.lectureStartTime}
        persona={persona}
      />

      {/* Central Railway Delay Certificate Modal */}
      <DelayCertificateModal
        isOpen={delayModalOpen}
        onClose={() => setDelayModalOpen(false)}
        tokenData={tokenData}
      />
    </article>
  );
};
