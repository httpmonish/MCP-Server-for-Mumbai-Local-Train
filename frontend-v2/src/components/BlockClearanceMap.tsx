import React, { useState, useEffect, useMemo } from 'react';
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

// Point helper
interface Point {
  x: number;
  y: number;
}

// Cubic Bezier interpolation
function getCubicBezierPoint(p0: Point, p1: Point, p2: Point, p3: Point, t: number): { point: Point; angle: number } {
  const mt = 1 - t;
  const mt2 = mt * mt;
  const mt3 = mt2 * mt;
  const t2 = t * t;
  const t3 = t2 * t;

  const x = mt3 * p0.x + 3 * mt2 * t * p1.x + 3 * mt * t2 * p2.x + t3 * p3.x;
  const y = mt3 * p0.y + 3 * mt2 * t * p1.y + 3 * mt * t2 * p2.y + t3 * p3.y;

  // Tangent derivative: B'(t) = 3(1-t)^2 (p1-p0) + 6(1-t)t (p2-p1) + 3t^2 (p3-p2)
  const dx = 3 * mt2 * (p1.x - p0.x) + 6 * mt * t * (p2.x - p1.x) + 3 * t2 * (p3.x - p2.x);
  const dy = 3 * mt2 * (p1.y - p0.y) + 6 * mt * t * (p2.y - p1.y) + 3 * t2 * (p3.y - p2.y);
  const angle = (Math.atan2(dy, dx) * 180) / Math.PI;

  return { point: { x, y }, angle };
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
  const [trainProgress, setTrainProgress] = useState(32); // 5% to 95%
  const [selectedStation, setSelectedStation] = useState<StationTelemetry | null>(null);
  const [showRakeDetails, setShowRakeDetails] = useState(false);
  const [isScrubbing, setIsScrubbing] = useState(false);

  // Smooth continuous train progression
  useEffect(() => {
    if (isScrubbing) return;
    const interval = setInterval(() => {
      setTrainProgress((prev) => {
        if (prev >= 94) return 6;
        return +(prev + 0.35).toFixed(2);
      });
    }, 100);
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

  // Track Curve Bezier Spline Nodes
  // Segment 1: (50, 95) -> (240, 55), (340, 135) -> (520, 95)
  // Segment 2: (520, 95) -> (680, 65), (820, 125) -> (950, 95)
  const trainCoord = useMemo(() => {
    // Normalise progress between 5 and 95
    const normalized = Math.max(0, Math.min(1, (trainProgress - 5) / 90));

    if (normalized <= 0.5) {
      const t = normalized / 0.5;
      return getCubicBezierPoint(
        { x: 50, y: 95 },
        { x: 240, y: 55 },
        { x: 340, y: 135 },
        { x: 520, y: 95 },
        t
      );
    } else {
      const t = (normalized - 0.5) / 0.5;
      return getCubicBezierPoint(
        { x: 520, y: 95 },
        { x: 680, y: 65 },
        { x: 820, y: 125 },
        { x: 950, y: 95 },
        t
      );
    }
  }, [trainProgress]);

  return (
    <section className="w-full relative rounded-3xl bg-white/[0.02] backdrop-blur-2xl border border-glass-border p-4 sm:p-6 overflow-hidden">
      {/* Ambient Volumetric Glows */}
      <div className="absolute -right-20 -top-20 w-80 h-80 rounded-full bg-primary/10 blur-[100px] pointer-events-none"></div>
      <div className="absolute -left-20 -bottom-20 w-80 h-80 rounded-full bg-secondary/10 blur-[100px] pointer-events-none"></div>

      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 mb-2">
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
            <span className="w-2 h-2 rounded-full bg-primary"></span> Signal Clear
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-secondary"></span> Caution (Double Amber)
          </span>
          <span className="hidden md:flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-surface-container-highest"></span> Occupied Block
          </span>
        </div>
      </div>

      {/* SVG Canvas with Clean Station Offsets and Small Moving EMU Train */}
      <div className="relative w-full py-2">
        <svg
          className="w-full h-44 sm:h-48 overflow-visible select-none"
          fill="none"
          viewBox="0 0 1000 190"
        >
          <defs>
            {/* Active Track Gradient */}
            <linearGradient id="trackGlowGrad" x1="0%" x2="100%" y1="0%" y2="0%">
              <stop offset="0%" stopColor="#4edea3" stopOpacity="0.95" />
              <stop offset="40%" stopColor="#4edea3" stopOpacity="0.9" />
              <stop offset="55%" stopColor="#ffb95f" stopOpacity="0.85" />
              <stop offset="85%" stopColor="#4edea3" stopOpacity="0.95" />
              <stop offset="100%" stopColor="#3c4a42" stopOpacity="0.4" />
            </linearGradient>

            {/* Neon Glow Filter */}
            <filter id="neonTrackGlow" x="-20%" y="-30%" width="140%" height="160%">
              <feGaussianBlur stdDeviation="3.5" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>

            {/* Train Headlight Beam Gradient */}
            <radialGradient id="headlightBeam" cx="100%" cy="50%" r="90%">
              <stop offset="0%" stopColor="#ffffff" stopOpacity="0.9" />
              <stop offset="40%" stopColor="#4edea3" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#4edea3" stopOpacity="0" />
            </radialGradient>
          </defs>

          {/* 1. Underlying Rail Bed (Track Bed Structure) */}
          <path
            d="M 50 95 C 240 55, 340 135, 520 95 C 680 65, 820 125, 950 95"
            fill="none"
            stroke="#15171a"
            strokeWidth="10"
            strokeLinecap="round"
          />

          {/* 2. Ballast Tie Markers */}
          <path
            d="M 50 95 C 240 55, 340 135, 520 95 C 680 65, 820 125, 950 95"
            fill="none"
            stroke="#262a30"
            strokeWidth="6"
            strokeDasharray="4 8"
            strokeLinecap="round"
          />

          {/* 3. High-Voltage Active Lit Track */}
          <path
            d="M 50 95 C 240 55, 340 135, 520 95 C 680 65, 820 125, 950 95"
            fill="none"
            filter="url(#neonTrackGlow)"
            stroke="url(#trackGlowGrad)"
            strokeWidth="3"
            strokeLinecap="round"
          />

          {/* ========================================================================= */}
          {/* STATION 1: THANE (X=50, Y=95) -> Label BELOW Track                       */}
          {/* ========================================================================= */}
          <g
            className="cursor-pointer group"
            onClick={() => setSelectedStation(currentStations[0] || defaultStationTelemetry[0])}
          >
            {/* Guide line down */}
            <line x1="50" y1="95" x2="50" y2="132" stroke="#4edea3" strokeWidth="1" strokeDasharray="2 2" opacity="0.6" />
            {/* Node Circle */}
            <circle cx="50" cy="95" r="7" fill="#090A0C" stroke="#4edea3" strokeWidth="3" className="group-hover:scale-125 transition-transform" />
            <circle cx="50" cy="95" r="2.5" fill="#4edea3" />

            {/* Label Container Below */}
            <text x="50" y="146" textAnchor="start" fill="#FFFFFF" fontSize="11" fontFamily="monospace" fontWeight="600">
              Thane
            </text>
            <text x="50" y="158" textAnchor="start" fill="#4edea3" fontSize="9" fontFamily="monospace">
              TNA • 0.0 km
            </text>
            <text x="50" y="170" textAnchor="start" fill="#717882" fontSize="8" fontFamily="sans-serif">
              PF 5 Ingress →
            </text>
          </g>

          {/* ========================================================================= */}
          {/* STATION 2: GHATKOPAR (X=275, Y=78) -> Label ABOVE Track                  */}
          {/* ========================================================================= */}
          <g
            className="cursor-pointer group"
            onClick={() => setSelectedStation(currentStations[1] || defaultStationTelemetry[1])}
          >
            {/* Guide line up */}
            <line x1="275" y1="78" x2="275" y2="42" stroke="#4edea3" strokeWidth="1" strokeDasharray="2 2" opacity="0.6" />
            {/* Node Circle */}
            <circle cx="275" cy="78" r="6" fill="#090A0C" stroke="#4edea3" strokeWidth="2.5" className="group-hover:scale-125 transition-transform" />
            <circle cx="275" cy="78" r="2" fill="#4edea3" />

            {/* Label Container Above */}
            <text x="275" y="24" textAnchor="middle" fill="#FFFFFF" fontSize="11" fontFamily="monospace" fontWeight="600">
              Ghatkopar
            </text>
            <text x="275" y="35" textAnchor="middle" fill="#4edea3" fontSize="9" fontFamily="monospace">
              GC • 19.8 km
            </text>
            <rect x="220" y="39" width="110" height="12" rx="6" fill="#ffffff" fillOpacity="0.06" />
            <text x="275" y="48" textAnchor="middle" fill="#9ca3af" fontSize="7.5" fontFamily="monospace">
              METRO 1 INTERCHANGE
            </text>
          </g>

          {/* ========================================================================= */}
          {/* STATION 3: KURLA JUNCTION (X=520, Y=95) -> Label BELOW Track             */}
          {/* ========================================================================= */}
          <g
            className="cursor-pointer group"
            onClick={() => setSelectedStation(currentStations[2] || defaultStationTelemetry[2])}
          >
            {/* Guide line down */}
            <line x1="520" y1="95" x2="520" y2="132" stroke="#ffb95f" strokeWidth="1" strokeDasharray="2 2" opacity="0.6" />
            {/* Node Circle */}
            <circle cx="520" cy="95" r="6.5" fill="#090A0C" stroke="#ffb95f" strokeWidth="2.5" className="group-hover:scale-125 transition-transform" />
            <circle cx="520" cy="95" r="2" fill="#ffb95f" />

            {/* Label Container Below */}
            <text x="520" y="146" textAnchor="middle" fill="#FFFFFF" fontSize="11" fontFamily="monospace" fontWeight="600">
              Kurla Junction
            </text>
            <text x="520" y="158" textAnchor="middle" fill="#ffb95f" fontSize="9" fontFamily="monospace">
              CLA • 24.7 km
            </text>
            <text x="520" y="170" textAnchor="middle" fill="#ffb95f" fontSize="8" fontFamily="monospace">
              Switch Speed: 30 km/h
            </text>
          </g>

          {/* ========================================================================= */}
          {/* STATION 4: DADAR / MATUNGA (X=745, Y=86) -> Label ABOVE Track            */}
          {/* ========================================================================= */}
          <g
            className="cursor-pointer group"
            onClick={() => setSelectedStation(currentStations[3] || defaultStationTelemetry[3])}
          >
            {/* Guide line up */}
            <line x1="745" y1="86" x2="745" y2="42" stroke="#4edea3" strokeWidth="1" strokeDasharray="2 2" opacity="0.6" />
            {/* Node Circle */}
            <circle cx="745" cy="86" r="7" fill="#090A0C" stroke="#4edea3" strokeWidth="3" className="group-hover:scale-125 transition-transform" />
            <circle cx="745" cy="86" r="2.5" fill="#4edea3" />

            {/* Label Container Above */}
            <text x="745" y="22" textAnchor="middle" fill="#FFFFFF" fontSize="11" fontFamily="monospace" fontWeight="600">
              Dadar / Matunga
            </text>
            <text x="745" y="33" textAnchor="middle" fill="#4edea3" fontSize="9" fontFamily="monospace">
              DR / MT • 29.2 km
            </text>
            <rect x="695" y="37" width="100" height="13" rx="6" fill="#4edea3" fillOpacity="0.15" />
            <text x="745" y="47" textAnchor="middle" fill="#4edea3" fontSize="8" fontFamily="monospace" fontWeight="bold">
              ★ VJTI DIRECT EXIT
            </text>
          </g>

          {/* ========================================================================= */}
          {/* STATION 5: CSMT TERMINUS (X=950, Y=95) -> Label BELOW Track              */}
          {/* ========================================================================= */}
          <g
            className="cursor-pointer group"
            onClick={() => setSelectedStation(currentStations[4] || defaultStationTelemetry[4])}
          >
            {/* Guide line down */}
            <line x1="950" y1="95" x2="950" y2="132" stroke="#717882" strokeWidth="1" strokeDasharray="2 2" opacity="0.6" />
            {/* Node Circle */}
            <circle cx="950" cy="95" r="6" fill="#090A0C" stroke="#3c4a42" strokeWidth="2" className="group-hover:scale-125 transition-transform" />
            <circle cx="950" cy="95" r="2" fill="#717882" />

            {/* Label Container Below */}
            <text x="950" y="146" textAnchor="end" fill="#d1d5db" fontSize="11" fontFamily="monospace" fontWeight="600">
              CSMT Terminus
            </text>
            <text x="950" y="158" textAnchor="end" fill="#9ca3af" fontSize="9" fontFamily="monospace">
              Terminus • 34 km
            </text>
          </g>

          {/* ========================================================================= */}
          {/* DYNAMIC MOVING MINI MUMBAI EMU LOCAL TRAIN RAKE                          */}
          {/* ========================================================================= */}
          <g
            transform={`translate(${trainCoord.point.x}, ${trainCoord.point.y}) rotate(${trainCoord.angle})`}
            className="cursor-pointer"
            onClick={() => setShowRakeDetails((prev) => !prev)}
          >
            {/* Forward Headlight Cone Beam */}
            <polygon
              points="18,-1 52,-14 52,14 18,1"
              fill="url(#headlightBeam)"
              opacity="0.85"
            />

            {/* Mini EMU Train Rake Body (3 Mini Coaches with Pantograph) */}
            {/* Rear Coach 3 */}
            <rect x="-38" y="-4.5" width="10" height="9" rx="1.5" fill="#1e2229" stroke="#4edea3" strokeWidth="0.8" />
            <rect x="-36" y="-2" width="2" height="4" fill="#4edea3" opacity="0.8" />
            <rect x="-32" y="-2" width="2" height="4" fill="#4edea3" opacity="0.8" />

            {/* Middle Coach 2 (Motor Coach with Pantograph) */}
            <rect x="-26" y="-4.5" width="11" height="9" rx="1.5" fill="#1e2229" stroke="#4edea3" strokeWidth="0.8" />
            {/* Pantograph */}
            <line x1="-22" y1="-4.5" x2="-20.5" y2="-8" stroke="#ffb95f" strokeWidth="1" />
            <line x1="-20.5" y1="-8" x2="-19" y2="-4.5" stroke="#ffb95f" strokeWidth="1" />
            <line x1="-23" y1="-8" x2="-18" y2="-8" stroke="#ffffff" strokeWidth="1" />
            <rect x="-24" y="-2" width="2.5" height="4" fill="#4edea3" opacity="0.8" />
            <rect x="-19.5" y="-2" width="2.5" height="4" fill="#4edea3" opacity="0.8" />

            {/* Front Driving Motor Cab (Coach 1) */}
            <path
              d="M -13 -4.5 L 14 -4.5 Q 18 -4.5 18 0 Q 18 4.5 14 4.5 L -13 4.5 Z"
              fill="#0d1117"
              stroke="#4edea3"
              strokeWidth="1.2"
            />
            {/* Green Central Railway Stripe */}
            <rect x="-11" y="2" width="25" height="1.8" fill="#4edea3" />
            {/* Windshield Glass */}
            <path d="M 8 -3 L 15 -3 Q 16.5 -3 16.5 0 Q 16.5 3 15 3 L 8 3 Z" fill="#38bdf8" opacity="0.9" />
            {/* Dual Twin Headlights */}
            <circle cx="17.5" cy="-2.2" r="1.2" fill="#ffffff" filter="drop-shadow(0 0 4px #ffffff)" />
            <circle cx="17.5" cy="2.2" r="1.2" fill="#ffffff" filter="drop-shadow(0 0 4px #ffffff)" />
          </g>
        </svg>

        {/* Compact Non-Overlapping Telemetry Badge that Hovers Above the Train */}
        <div
          style={{
            left: `${((trainCoord.point.x - 20) / 960) * 100}%`,
            top: `${Math.max(10, (trainCoord.point.y / 190) * 100 - 32)}%`,
          }}
          className="absolute -translate-x-1/2 pointer-events-auto cursor-pointer z-30 transition-all duration-150"
          onClick={() => setShowRakeDetails((prev) => !prev)}
        >
          <div className="relative group">
            <div className="px-2.5 py-1 rounded-full bg-surface-obsidian/95 backdrop-blur-xl border border-primary/50 shadow-[0_0_15px_rgba(78,222,163,0.3)] flex items-center gap-2 whitespace-nowrap hover:scale-105 transition-transform">
              <span className="w-2 h-2 rounded-full bg-primary animate-ping"></span>
              <span className="font-mono text-[11px] text-text-primary font-bold">
                {activeRake.trainNumber}
              </span>
              <span className="font-mono text-[10px] text-primary font-semibold">
                {activeRake.speed}
              </span>
              <span className="hidden sm:inline font-mono text-[9px] text-text-muted">
                • {activeRake.signal}
              </span>
            </div>

            {/* Extended Detail Inspection Card when Clicked */}
            {showRakeDetails && (
              <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 p-3 rounded-2xl bg-surface-obsidian/98 border border-primary/60 shadow-2xl text-[11px] font-mono text-text-primary flex flex-col gap-1 z-40 whitespace-nowrap">
                <div className="flex items-center justify-between gap-3 pb-1 border-b border-white/[0.08]">
                  <span className="text-primary font-bold">{activeRake.trainNumber} LIVE INSPECTION</span>
                  <span className="text-text-muted text-[10px]">Headway: {activeRake.headway}</span>
                </div>
                <div className="text-[10px] text-text-secondary">
                  <span>Speed: <strong className="text-primary">{activeRake.speed}</strong></span>
                  <span className="mx-1.5">•</span>
                  <span>Signal: <strong className="text-primary">{activeRake.signal}</strong></span>
                </div>
                <div className="text-[9px] text-text-muted">
                  Dwell: 22s • Automatic Door Interlock Active
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Scrub Bar & Control Slider */}
      <div className="mt-2 pt-3 border-t border-glass-border flex flex-col sm:flex-row items-center justify-between gap-3 font-mono text-[10px] text-text-muted">
        <div className="flex items-center gap-2">
          <span>Live Coordinate:</span>
          <span className="text-primary font-bold">{trainProgress.toFixed(1)}% along Corridor</span>
          <span className="text-text-muted">• Speed: {activeRake.speed}</span>
        </div>

        <div className="flex items-center gap-3 w-full sm:w-64">
          <span className="text-text-muted">TNA</span>
          <input
            type="range"
            min={5}
            max={95}
            step={0.2}
            value={trainProgress}
            onMouseDown={() => setIsScrubbing(true)}
            onMouseUp={() => setIsScrubbing(false)}
            onTouchStart={() => setIsScrubbing(true)}
            onTouchEnd={() => setIsScrubbing(false)}
            onChange={(e) => setTrainProgress(parseFloat(e.target.value))}
            className="w-full accent-primary h-1.5 bg-white/[0.1] rounded-lg cursor-pointer"
          />
          <span className="text-text-muted">CSMT</span>
        </div>

        <span className="text-text-secondary hidden md:inline">
          Click station nodes or train rake for live platform status
        </span>
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
