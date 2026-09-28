import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { TrainRakeTelemetry } from '../lib/services/telemetryService';
import type { PersonaType } from './modals/UserProfilePopover';

interface LiveRakeListProps {
  rakes: TrainRakeTelemetry[];
  selectedRakeId: string;
  onSelectRake: (rakeId: string) => void;
  isLoading?: boolean;
  persona?: PersonaType;
}

export const LiveRakeList: React.FC<LiveRakeListProps> = ({
  rakes,
  selectedRakeId,
  onSelectRake,
  isLoading = false,
  persona = 'COMMUTER',
}) => {
  const [expandedRake, setExpandedRake] = useState<string | null>('95401-stops');
  const [hoveredCoach, setHoveredCoach] = useState<string | null>(null);
  const [verifiedPassId, setVerifiedPassId] = useState<string | null>(null);

  const handleVerifyPass = (rakeId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setVerifiedPassId(rakeId);
    setTimeout(() => setVerifiedPassId(null), 5000);
  };

  return (
    <section className="flex flex-col gap-4">
      {/* Section Header */}
      <div className="flex items-end justify-between px-1 pb-2">
        <div className="flex flex-col">
          <span className="font-mono text-[11px] uppercase text-text-muted tracking-widest">
            Suburban Local & Fast Telemetry
          </span>
          <div className="flex items-baseline gap-2 mt-0.5">
            <h2 className="font-headline text-3xl tracking-tight text-text-primary">Today’s Flow</h2>
            <span className="font-headline-italic italic text-xl text-text-secondary">
              {persona === 'STUDENT'
                ? 'VJTI Academic Corridors'
                : persona === 'CORPORATE'
                ? 'Corporate Office Corridors'
                : 'Mumbai Suburban Corridors'}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-3 py-1 rounded-full bg-white/[0.04] border border-glass-border font-mono text-[11px] text-text-secondary">
            {rakes.length} Rakes in 28m Window
          </span>
        </div>
      </div>

      {/* Loading Skeleton */}
      {isLoading ? (
        <div className="flex flex-col gap-4">
          {[1, 2, 3].map((n) => (
            <div
              key={n}
              className="w-full h-48 rounded-3xl bg-white/[0.02] border border-glass-border animate-pulse p-6 flex flex-col justify-between"
            >
              <div className="flex items-center justify-between">
                <div className="w-32 h-6 bg-white/[0.06] rounded-full"></div>
                <div className="w-24 h-6 bg-white/[0.06] rounded-full"></div>
              </div>
              <div className="w-64 h-10 bg-white/[0.06] rounded-xl"></div>
              <div className="grid grid-cols-3 gap-2">
                <div className="h-8 bg-white/[0.04] rounded-xl"></div>
                <div className="h-8 bg-white/[0.04] rounded-xl"></div>
                <div className="h-8 bg-white/[0.04] rounded-xl"></div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        /* Rakes List */
        rakes.map((rake) => {
          const isSelected = selectedRakeId === rake.id;
          const isDelayed = rake.status === 'DELAYED';
          const isAC = rake.trainType === 'AC_FAST';

          return (
            <motion.article
              key={rake.id}
              layout
              onClick={() => onSelectRake(rake.id)}
              whileHover={{ y: -2 }}
              className={`w-full rounded-3xl backdrop-blur-2xl p-4 sm:p-6 transition-all duration-300 shadow-xl flex flex-col gap-4 cursor-pointer relative overflow-hidden ${
                isSelected
                  ? 'bg-white/[0.06] border-2 border-primary/50 shadow-[0_0_30px_rgba(78,222,163,0.15)]'
                  : 'bg-white/[0.03] border border-glass-border hover:bg-white/[0.05] hover:border-glass-border-hover'
              }`}
            >
              {/* Selected Glow Indicator */}
              {isSelected && (
                <div className="absolute top-0 right-0 w-2 h-full bg-primary shadow-[0_0_12px_#4edea3]"></div>
              )}

              {/* Top Telemetry Row */}
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <span
                    className={`px-2.5 py-1 rounded-full font-mono text-[11px] uppercase flex items-center gap-1.5 font-semibold ${
                      isDelayed
                        ? 'bg-secondary/20 text-secondary'
                        : 'bg-primary/10 text-primary'
                    }`}
                  >
                    <span
                      className={`w-1.5 h-1.5 rounded-full ${
                        isDelayed ? 'bg-secondary animate-pulse' : 'bg-primary animate-ping'
                      }`}
                    ></span>
                    {isDelayed ? `Delayed +${rake.delayMinutes}m` : 'On Schedule'}
                  </span>

                  <span className="px-2.5 py-1 rounded-full bg-white/[0.04] text-text-secondary font-mono text-[11px]">
                    {rake.trainNumber}
                  </span>

                  <span className="hidden sm:inline font-mono text-[11px] text-text-muted">
                    • {isAC ? 'Medha Plug-Door AC Rake' : '12-Car Suburban Siemens EMU'}
                  </span>

                  {isSelected && (
                    <span className="font-mono text-[10px] px-2 py-0.5 rounded-full bg-primary/20 text-primary font-bold">
                      ACTIVE TRACKED
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-3 font-mono text-[11px] text-text-secondary">
                  <span className="flex items-center gap-1 text-primary">
                    <span className="material-symbols-outlined text-[16px]">speed</span>
                    {rake.currentSpeedKm} km/h
                  </span>
                  <span className="text-text-muted">•</span>
                  <span className="px-2 py-0.5 rounded-full bg-white/[0.04]">{rake.platform}</span>
                </div>
              </div>

              {/* Times & Destinations */}
              <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-3 py-1">
                <div className="flex items-baseline gap-3">
                  <div className="flex items-baseline gap-1.5">
                    <span className="font-headline text-3xl text-text-primary tracking-tight font-normal">
                      {rake.departureTime}
                    </span>
                    {isDelayed && (
                      <span className="font-mono text-xs text-secondary line-through">09:02</span>
                    )}
                  </div>
                  <span className="font-body text-sm text-text-muted font-light">{rake.originCode} Dep</span>
                  <span className="material-symbols-outlined text-text-muted text-[18px] translate-y-0.5">
                    trending_flat
                  </span>
                  <span
                    className={`font-headline text-3xl tracking-tight font-normal ${
                      isDelayed ? 'text-text-secondary' : 'text-primary'
                    }`}
                  >
                    {rake.arrivalTime}
                  </span>
                  <span className="font-body text-sm text-text-muted font-light">{rake.destinationCode} Arr</span>
                </div>

                <div className="flex flex-col sm:items-end">
                  <span className="font-mono text-lg text-text-primary font-medium tracking-tight">
                    {rake.durationMins} mins
                  </span>
                  <span className="font-body text-xs text-text-muted">
                    {rake.stopsCount} Stops ({rake.viaDescription})
                  </span>
                </div>
              </div>

              {/* Occupancy & Commuter Target Delta */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-1">
                <div className="p-3 rounded-2xl bg-white/[0.02] border border-glass-border flex items-center justify-between">
                  <span className="font-body text-xs text-text-muted">Total Load</span>
                  <span
                    className={`font-mono text-xs font-medium ${
                      rake.totalLoadPercent > 85 ? 'text-secondary' : 'text-primary'
                    }`}
                  >
                    {rake.totalLoadPercent}% ({rake.totalLoadPercent > 85 ? 'Heavy Density' : 'Comfortable'})
                  </span>
                </div>
                <div className="p-3 rounded-2xl bg-white/[0.02] border border-glass-border flex items-center justify-between">
                  <span className="font-body text-xs text-text-muted">
                    {persona === 'STUDENT' ? 'VJTI Walk' : 'Destination Egress'}
                  </span>
                  <span className="font-mono text-xs text-text-primary font-medium">
                    {persona === 'STUDENT' ? '6 mins to Mechanical Bldg' : '5 mins walk to concourse exit'}
                  </span>
                </div>
                <div className="p-3 rounded-2xl bg-white/[0.02] border border-glass-border flex items-center justify-between">
                  <span className="font-body text-xs text-text-muted">Transit Buffer</span>
                  <span
                    className={`font-mono text-xs font-semibold ${
                      rake.targetDeltaMins > 0 ? 'text-primary' : 'text-secondary'
                    }`}
                  >
                    {rake.arrivalBufferText}
                  </span>
                </div>
              </div>

              {/* UTS Pass Verification Status Banner */}
              {verifiedPassId === rake.id && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-3 rounded-2xl bg-primary/10 border border-primary/30 flex items-center justify-between font-mono text-xs text-primary"
                >
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-[18px]">verified</span>
                    <span>UTS Suburban Season Ticket #CR-98401 Active • Valid across all lines</span>
                  </div>
                  <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-primary text-black">
                    Active
                  </span>
                </motion.div>
              )}

              {/* Carriage Crowding Matrix & Station-by-Station Timetable Accordion */}
              <div className="w-full pt-1">
                <div className="flex items-center gap-2 mb-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setExpandedRake(expandedRake === `${rake.id}-stops` ? null : `${rake.id}-stops`);
                    }}
                    className={`flex-1 py-2 px-3 rounded-2xl border transition-all flex items-center justify-between font-body text-xs cursor-pointer ${
                      expandedRake === `${rake.id}-stops`
                        ? 'bg-primary/10 border-primary/40 text-primary font-semibold'
                        : 'bg-white/[0.02] hover:bg-white/[0.05] border-glass-border text-text-secondary hover:text-text-primary'
                    }`}
                  >
                    <span className="flex items-center gap-2">
                      <span className="material-symbols-outlined text-[18px]">schedule</span>
                      <span>Station Stops Timetable ({rake.stops?.length || rake.stopsCount} Stops)</span>
                    </span>
                    <span className="material-symbols-outlined text-[16px]">
                      {expandedRake === `${rake.id}-stops` ? 'expand_less' : 'expand_more'}
                    </span>
                  </button>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setExpandedRake(expandedRake === `${rake.id}-coaches` ? null : `${rake.id}-coaches`);
                    }}
                    className={`flex-1 py-2 px-3 rounded-2xl border transition-all flex items-center justify-between font-body text-xs cursor-pointer ${
                      expandedRake === `${rake.id}-coaches`
                        ? 'bg-primary/10 border-primary/40 text-primary font-semibold'
                        : 'bg-white/[0.02] hover:bg-white/[0.05] border-glass-border text-text-secondary hover:text-text-primary'
                    }`}
                  >
                    <span className="flex items-center gap-2">
                      <span className="material-symbols-outlined text-[18px]">view_column</span>
                      <span>12-Coach Crowd Matrix</span>
                    </span>
                    <span className="material-symbols-outlined text-[16px]">
                      {expandedRake === `${rake.id}-coaches` ? 'expand_less' : 'expand_more'}
                    </span>
                  </button>
                </div>

                {/* 1. Station-by-Station Timetable View */}
                <AnimatePresence>
                  {expandedRake === `${rake.id}-stops` && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="flex flex-col gap-2 pt-2 px-1 overflow-hidden"
                    >
                      <div className="p-3 rounded-2xl bg-surface-container-high/60 border border-glass-border flex flex-col gap-2">
                        <div className="flex items-center justify-between pb-2 border-b border-white/[0.06] font-mono text-[10px] text-text-muted uppercase">
                          <span>Station / Platform</span>
                          <div className="flex items-center gap-6">
                            <span>Arrival</span>
                            <span>Departure</span>
                            <span>Chainage</span>
                          </div>
                        </div>

                        <div className="flex flex-col gap-1.5 max-h-56 overflow-y-auto pr-1">
                          {rake.stops?.map((stop, idx) => {
                            const isFirst = idx === 0;
                            const isLast = idx === (rake.stops?.length || 1) - 1;

                            return (
                              <div
                                key={`stop-${stop.stationCode}-${idx}`}
                                className={`px-3 py-2 rounded-xl border transition-colors flex items-center justify-between font-mono text-xs ${
                                  isFirst || isLast
                                    ? 'bg-primary/10 border-primary/30 text-primary font-bold'
                                    : 'bg-white/[0.02] border-transparent hover:border-glass-border text-text-primary'
                                }`}
                              >
                                <div className="flex items-center gap-2.5">
                                  <span
                                    className={`w-2 h-2 rounded-full ${
                                      isFirst ? 'bg-primary animate-ping' : isLast ? 'bg-secondary' : 'bg-primary/60'
                                    }`}
                                  ></span>
                                  <div className="flex flex-col text-left">
                                    <span className="font-semibold text-text-primary">
                                      {stop.stationName} <span className="text-[10px] text-primary">[{stop.stationCode}]</span>
                                    </span>
                                    <span className="text-[9px] text-text-muted">
                                      {stop.platform} • {stop.dwellSeconds ? `${stop.dwellSeconds}s Dwell` : isLast ? 'Terminus' : 'Origin'}
                                    </span>
                                  </div>
                                </div>

                                <div className="flex items-center gap-6 text-right">
                                  <span className="text-text-secondary w-14">
                                    {isFirst ? '--:--' : stop.arrivalTime}
                                  </span>
                                  <span className="text-text-primary font-semibold w-14">
                                    {isLast ? '--:--' : stop.departureTime}
                                  </span>
                                  <span className="text-text-muted text-[10px] w-12 text-right">
                                    {stop.distanceKm.toFixed(1)} km
                                  </span>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* 2. Expandable 12-Coach Matrix */}
                <AnimatePresence>
                  {expandedRake === `${rake.id}-coaches` && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="flex flex-col gap-3 pt-2 px-1 overflow-hidden"
                    >
                      <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-2">
                        {rake.coachMatrix.map((coach) => (
                          <div
                            key={coach.coachNumber}
                            onMouseEnter={() => setHoveredCoach(`${rake.id}-${coach.coachNumber}`)}
                            onMouseLeave={() => setHoveredCoach(null)}
                            className="p-2.5 rounded-xl bg-surface-container-high/70 border border-glass-border hover:border-primary/50 transition-all flex flex-col gap-1.5 relative group/coach"
                          >
                            <div className="flex items-center justify-between">
                              <span className="font-mono text-[11px] text-text-primary font-medium">
                                C{coach.coachNumber} {coach.coachType === 'FIRST_CLASS' ? 'FC' : coach.coachType === 'LADIES' ? 'LD' : coach.coachType === 'AC' ? 'AC' : 'GEN'}
                              </span>
                              <span
                                className={`font-mono text-[10px] font-bold ${
                                  coach.crowdPercent > 80 ? 'text-secondary' : 'text-primary'
                                }`}
                              >
                                {coach.crowdPercent}%
                              </span>
                            </div>

                            <div className="w-full bg-white/[0.06] h-1.5 rounded-full overflow-hidden">
                              <div
                                className={`h-full rounded-full ${
                                  coach.crowdPercent > 80 ? 'bg-secondary' : 'bg-primary'
                                }`}
                                style={{ width: `${coach.crowdPercent}%` }}
                              ></div>
                            </div>

                            <span className="font-mono text-[9px] text-text-muted truncate">
                              {coach.description}
                            </span>

                            {/* Coach Hover Tooltip */}
                            {hoveredCoach === `${rake.id}-${coach.coachNumber}` && (
                              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-30 p-2 rounded-xl bg-surface-obsidian border border-glass-border shadow-2xl text-[10px] font-mono text-text-primary whitespace-nowrap pointer-events-none">
                                <span className="text-primary font-bold">Coach #{coach.coachNumber}:</span> {coach.fobAlignmentText}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>

                      <div className="flex flex-col sm:flex-row items-center justify-between font-mono text-[11px] text-text-muted pt-1 gap-2">
                        <span>Predictive Flow Telemetry V3.2 • Hover coach to inspect platform staircase alignment</span>
                        <button
                          onClick={(e) => handleVerifyPass(rake.id, e)}
                          className="text-primary hover:underline cursor-pointer flex items-center gap-1 font-semibold"
                        >
                          Verify Pass Validity →
                        </button>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.article>
          );
        })
      )}
    </section>
  );
};
