import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import type { StationTelemetry } from '../lib/services/telemetryService';
import { StationInspectionDrawer } from './modals/StationInspectionDrawer';

interface BlockClearanceMapProps {
  sectionTitle?: string;
  activeRake?: {
    trainNumber: string;
    speed: string;
    signal: string;
    headway: string;
  };
  stations?: StationTelemetry[];
}

export const BlockClearanceMap: React.FC<BlockClearanceMapProps> = ({
  sectionTitle = 'Section: TNA-DR Quad-Track (Down Through)',
  activeRake = {
    trainNumber: '#95401 FAST',
    speed: '92 km/h',
    signal: 'Sig S-44 Clear',
    headway: 'Headway 3m 40s',
  },
  stations = [],
}) => {
  const [trainProgress, setTrainProgress] = useState(38); // 0 to 100%
  const [selectedStation, setSelectedStation] = useState<StationTelemetry | null>(null);
  const [showRakeDetails, setShowRakeDetails] = useState(false);
  const [isScrubbing, setIsScrubbing] = useState(false);

  // Train auto movement simulation
  useEffect(() => {
    if (isScrubbing) return;
    const interval = setInterval(() => {
      setTrainProgress((prev) => (prev >= 92 ? 10 : prev + 0.8));
    }, 1500);
    return () => clearInterval(interval);
  }, [isScrubbing]);

  const defaultStationTelemetry: StationTelemetry[] = [
    {
      code: 'TNA',
      name: 'Thane',
      distanceKm: 0.0,
      platforms: [
        { number: '01', occupancyPercent: 88, fobCongestion: 'HIGH', crossoverSpeedKm: 30 },
        { number: '05', occupancyPercent: 78, fobCongestion: 'MODERATE', crossoverSpeedKm: 45 },
      ],
    },
    {
      code: 'GC',
      name: 'Ghatkopar',
      distanceKm: 19.8,
      platforms: [
        { number: '01', occupancyPercent: 94, fobCongestion: 'CRITICAL', crossoverSpeedKm: 30 },
      ],
    },
    {
      code: 'CLA',
      name: 'Kurla Junction',
      distanceKm: 24.7,
      platforms: [
        { number: '01', occupancyPercent: 90, fobCongestion: 'CRITICAL', crossoverSpeedKm: 30 },
        { number: '05', occupancyPercent: 70, fobCongestion: 'MODERATE', crossoverSpeedKm: 40 },
      ],
    },
    {
      code: 'DR',
      name: 'Dadar / Matunga',
      distanceKm: 29.2,
      platforms: [
        { number: '01', occupancyPercent: 74, fobCongestion: 'MODERATE', crossoverSpeedKm: 45 },
        { number: '04', occupancyPercent: 68, fobCongestion: 'LOW', crossoverSpeedKm: 45 },
      ],
    },
    {
      code: 'CSMT',
      name: 'CSMT Terminus',
      distanceKm: 34.0,
      platforms: [
        { number: '01', occupancyPercent: 60, fobCongestion: 'LOW', crossoverSpeedKm: 25 },
      ],
    },
  ];

  const currentStations = stations.length > 0 ? stations : defaultStationTelemetry;

  return (
    <section className="w-full relative rounded-3xl bg-white/[0.02] backdrop-blur-2xl border border-glass-border p-4 sm:p-6 overflow-hidden">
      {/* Ambient Backlight Glows */}
      <div className="absolute -right-20 -top-20 w-80 h-80 rounded-full bg-primary/10 blur-[100px] pointer-events-none"></div>
      <div className="absolute -left-20 -bottom-20 w-80 h-80 rounded-full bg-secondary/10 blur-[100px] pointer-events-none"></div>

      {/* Title & Telemetry Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 mb-4">
        <div className="flex items-center gap-2">
          <span className="font-mono text-[11px] uppercase text-primary tracking-widest flex items-center gap-1.5 font-semibold">
            <span className="w-2 h-2 rounded-full bg-primary animate-ping"></span>
            TMS Block Clearance Telemetry
          </span>
          <span className="text-text-muted">•</span>
          <span className="font-mono text-[11px] text-text-muted">{sectionTitle}</span>
        </div>
        <div className="flex items-center gap-4 font-mono text-[11px] text-text-secondary">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-primary"></span> Signal Clear (Green)
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-secondary"></span> Caution (Double Amber)
          </span>
          <span className="hidden md:flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-surface-container-highest"></span> Occupied Block
          </span>
        </div>
      </div>

      {/* Vector Curved SVG Topology with Animated Interactive Track */}
      <div className="relative w-full py-4 sm:py-6">
        <svg
          className="w-full h-32 overflow-visible"
          fill="none"
          preserveAspectRatio="none"
          viewBox="0 0 1000 120"
        >
          <defs>
            <linearGradient id="trackGradient" x1="0%" x2="100%" y1="0%" y2="0%">
              <stop offset="0%" stopColor="#4edea3" stopOpacity="0.9" />
              <stop offset="35%" stopColor="#4edea3" stopOpacity="0.8" />
              <stop offset="55%" stopColor="#4edea3" stopOpacity="0.9" />
              <stop offset="80%" stopColor="#ffb95f" stopOpacity="0.6" />
              <stop offset="100%" stopColor="#3c4a42" stopOpacity="0.3" />
            </linearGradient>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="4" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Shadow Guide Wire */}
          <path
            d="M 40 60 C 220 20, 320 100, 520 60 C 680 30, 820 90, 960 60"
            fill="none"
            stroke="#1f2022"
            strokeLinecap="round"
            strokeWidth="6"
          />
          {/* Active Lit Rail Line */}
          <path
            d="M 40 60 C 220 20, 320 100, 520 60 C 680 30, 820 90, 960 60"
            fill="none"
            filter="url(#glow)"
            stroke="url(#trackGradient)"
            strokeLinecap="round"
            strokeWidth="2.5"
          />

          {/* Interactive Station Clearance Nodes */}
          {/* Station 1: Thane (0 km) */}
          <circle
            cx="40"
            cy="60"
            r="8"
            fill="#090A0C"
            stroke="#4edea3"
            strokeWidth="3.5"
            className="cursor-pointer hover:stroke-white transition-all"
            onClick={() => setSelectedStation(currentStations[0] || defaultStationTelemetry[0])}
          />
          {/* Station 2: Ghatkopar (19.8 km) */}
          <circle
            cx="280"
            cy="46"
            r="7"
            fill="#090A0C"
            stroke="#4edea3"
            strokeWidth="3"
            className="cursor-pointer hover:stroke-white transition-all"
            onClick={() => setSelectedStation(currentStations[1] || defaultStationTelemetry[1])}
          />
          {/* Station 3: Kurla Junction (24.7 km) */}
          <circle
            cx="520"
            cy="60"
            r="7"
            fill="#090A0C"
            stroke="#ffb95f"
            strokeWidth="3"
            className="cursor-pointer hover:stroke-white transition-all"
            onClick={() => setSelectedStation(currentStations[2] || defaultStationTelemetry[2])}
          />
          {/* Station 4: Matunga / Dadar (29.2 km) */}
          <circle
            cx="760"
            cy="56"
            r="8"
            fill="#090A0C"
            stroke="#4edea3"
            strokeWidth="3.5"
            className="cursor-pointer hover:stroke-white transition-all"
            onClick={() => setSelectedStation(currentStations[3] || defaultStationTelemetry[3])}
          />
          {/* Station 5: CSMT Terminus (34.0 km) */}
          <circle
            cx="960"
            cy="60"
            r="7"
            fill="#090A0C"
            stroke="#3c4a42"
            strokeWidth="2.5"
            className="cursor-pointer hover:stroke-white transition-all"
            onClick={() => setSelectedStation(currentStations[4] || defaultStationTelemetry[4])}
          />
        </svg>

        {/* Positioned Overlay Metadata Labels for Station Nodes */}
        <div className="absolute inset-0 pointer-events-none flex justify-between px-2 sm:px-4">
          {/* Thane Node */}
          <div
            onClick={() => setSelectedStation(currentStations[0] || defaultStationTelemetry[0])}
            className="flex flex-col items-start pt-16 pointer-events-auto cursor-pointer group"
          >
            <span className="font-mono text-xs text-text-primary group-hover:text-primary font-medium tracking-tight">
              {currentStations[0]?.name || 'Thane'}
            </span>
            <div className="flex items-center gap-1 font-mono text-[10px] text-primary">
              <span>{currentStations[0]?.code || 'TNA'}</span>
              <span className="text-text-muted">• 0.0 km</span>
            </div>
            <span className="text-[9px] text-text-muted group-hover:underline">View Platform Status →</span>
          </div>

          {/* Ghatkopar Node */}
          <div
            onClick={() => setSelectedStation(currentStations[1] || defaultStationTelemetry[1])}
            className="flex flex-col items-center -mt-2 sm:-mt-1 translate-x-2 pointer-events-auto cursor-pointer group"
          >
            <span className="font-mono text-xs text-text-primary group-hover:text-primary font-medium tracking-tight">
              {currentStations[1]?.name || 'Ghatkopar'}
            </span>
            <div className="flex items-center gap-1 font-mono text-[10px] text-text-secondary">
              <span>{currentStations[1]?.code || 'GC'}</span>
              <span className="text-text-muted">• 19.8 km</span>
            </div>
            <span className="mt-1 font-mono text-[9px] uppercase px-2 py-0.5 rounded-full bg-white/[0.04] text-text-muted group-hover:bg-primary/20 group-hover:text-primary">
              Metro Line 1 Interconnect
            </span>
          </div>

          {/* Kurla Jcn Node */}
          <div
            onClick={() => setSelectedStation(currentStations[2] || defaultStationTelemetry[2])}
            className="flex flex-col items-center pt-16 -translate-x-3 pointer-events-auto cursor-pointer group"
          >
            <span className="font-mono text-xs text-text-primary group-hover:text-secondary font-medium tracking-tight">
              {currentStations[2]?.name || 'Kurla Jcn'}
            </span>
            <div className="flex items-center gap-1 font-mono text-[10px] text-secondary">
              <span>{currentStations[2]?.code || 'CLA'}</span>
              <span className="text-text-muted">• 24.7 km</span>
            </div>
            <span className="font-mono text-[10px] text-secondary">Switch Speed: 30 km/h</span>
          </div>

          {/* Dadar / VJTI Node */}
          <div
            onClick={() => setSelectedStation(currentStations[3] || defaultStationTelemetry[3])}
            className="flex flex-col items-center -mt-2 sm:-mt-1 -translate-x-6 pointer-events-auto cursor-pointer group"
          >
            <div className="flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-primary"></span>
              <span className="font-mono text-xs text-text-primary group-hover:text-primary font-medium tracking-tight">
                {currentStations[3]?.name || 'Dadar / Matunga'}
              </span>
            </div>
            <div className="flex items-center gap-1 font-mono text-[10px] text-primary">
              <span>{currentStations[3]?.code || 'DR'}</span>
              <span className="text-text-muted">• 29.2 km</span>
            </div>
            <span className="mt-1 font-mono text-[9px] uppercase px-2 py-0.5 rounded-full bg-primary/10 text-primary">
              VJTI Direct Exit
            </span>
          </div>

          {/* CSMT Node */}
          <div
            onClick={() => setSelectedStation(currentStations[4] || defaultStationTelemetry[4])}
            className="hidden md:flex flex-col items-end pt-16 pointer-events-auto cursor-pointer group"
          >
            <span className="font-mono text-xs text-text-secondary group-hover:text-text-primary font-medium tracking-tight">
              {currentStations[4]?.name || 'CSMT'}
            </span>
            <div className="flex items-center gap-1 font-mono text-[10px] text-text-muted">
              <span>Terminus</span>
              <span>• 34 km</span>
            </div>
          </div>
        </div>

        {/* Train Rake `#95401 FAST` Dynamic Stepper with Spring Physics */}
        <motion.div
          style={{ left: `${trainProgress}%` }}
          transition={{ type: 'spring', damping: 20, stiffness: 200 }}
          className="absolute top-1/2 -translate-y-14 sm:-translate-y-16 -translate-x-1/2 pointer-events-auto cursor-pointer z-20 group"
          onClick={() => setShowRakeDetails((prev) => !prev)}
        >
          <div className="relative">
            <span className="absolute inset-0 rounded-2xl bg-primary/40 blur-md animate-pulse"></span>
            <div className="relative px-3.5 py-2 rounded-2xl bg-surface-obsidian/95 backdrop-blur-xl border border-glass-border shadow-2xl flex items-center gap-3 hover:border-primary/50 transition-all">
              <div className="w-2.5 h-2.5 rounded-full bg-primary shadow-[0_0_10px_#4edea3] shrink-0 animate-ping"></div>
              <div className="flex flex-col">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs text-text-primary font-bold">
                    {activeRake.trainNumber}
                  </span>
                  <span className="font-mono text-[9px] uppercase px-1.5 py-0.5 rounded bg-primary/20 text-primary font-semibold">
                    Live Rake
                  </span>
                </div>
                <div className="flex items-center gap-2 font-mono text-[10px] text-text-secondary whitespace-nowrap">
                  <span className="text-primary font-medium">{activeRake.speed}</span>
                  <span className="text-text-muted">•</span>
                  <span>{activeRake.signal}</span>
                  <span className="text-text-muted">•</span>
                  <span className="text-primary font-medium">{activeRake.headway}</span>
                </div>
              </div>
            </div>
            <div className="w-2 h-2 bg-surface-obsidian/95 rotate-45 mx-auto -mt-1 shadow-md border-r border-b border-glass-border"></div>
            {showRakeDetails && (
              <div className="absolute top-full left-1/2 -translate-x-1/2 mt-2 p-2.5 rounded-xl bg-surface-obsidian/95 border border-primary/40 shadow-2xl text-[10px] font-mono text-text-primary whitespace-nowrap z-30">
                <span className="text-primary font-bold">Inspection:</span> Dwell Time 25s • Track Circuit Clear • Motorman Link Active
              </div>
            )}
          </div>
        </motion.div>
      </div>

      {/* Track Scrub Bar & Live Progress Slider */}
      <div className="mt-6 pt-3 border-t border-glass-border flex items-center justify-between gap-4 font-mono text-[10px] text-text-muted">
        <div className="flex items-center gap-2">
          <span>Live Coordinate:</span>
          <span className="text-primary font-bold">{trainProgress.toFixed(1)}% along Corridor</span>
        </div>
        <div className="flex items-center gap-3 flex-1 max-w-xs">
          <span className="text-text-muted">Origin</span>
          <input
            type="range"
            min={5}
            max={95}
            step={0.5}
            value={trainProgress}
            onMouseDown={() => setIsScrubbing(true)}
            onMouseUp={() => setIsScrubbing(false)}
            onChange={(e) => setTrainProgress(parseFloat(e.target.value))}
            className="w-full accent-primary h-1 bg-white/[0.1] rounded-lg cursor-pointer"
          />
          <span className="text-text-muted">Dadar</span>
        </div>
        <span className="hidden sm:inline text-text-secondary">Click station nodes or train badge to inspect</span>
      </div>

      {/* Station Clearance Node Inspection Drawer */}
      <StationInspectionDrawer
        isOpen={Boolean(selectedStation)}
        onClose={() => setSelectedStation(null)}
        station={selectedStation}
      />
    </section>
  );
};
