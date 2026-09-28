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

interface Point {
  x: number;
  y: number;
}

function getCubicBezierPoint(p0: Point, p1: Point, p2: Point, p3: Point, t: number): { point: Point; angle: number } {
  const mt = 1 - t;
  const mt2 = mt * mt;
  const mt3 = mt2 * mt;
  const t2 = t * t;
  const t3 = t2 * t;

  const x = mt3 * p0.x + 3 * mt2 * t * p1.x + 3 * mt * t2 * p2.x + t3 * p3.x;
  const y = mt3 * p0.y + 3 * mt2 * t * p1.y + 3 * mt * t2 * p2.y + t3 * p3.y;

  const dx = 3 * mt2 * (p1.x - p0.x) + 6 * mt * t * (p2.x - p1.x) + 3 * t2 * (p3.x - p2.x);
  const dy = 3 * mt2 * (p1.y - p0.y) + 6 * mt * t * (p2.y - p1.y) + 3 * t2 * (p3.y - p2.y);
  const angle = (Math.atan2(dy, dx) * 180) / Math.PI;

  return { point: { x, y }, angle };
}

function evaluateTrackSpline(tNorm: number): { point: Point; angle: number } {
  const clamped = Math.max(0, Math.min(1, tNorm));
  if (clamped <= 0.5) {
    const t = clamped / 0.5;
    return getCubicBezierPoint(
      { x: 50, y: 95 },
      { x: 240, y: 55 },
      { x: 340, y: 135 },
      { x: 520, y: 95 },
      t
    );
  } else {
    const t = (clamped - 0.5) / 0.5;
    return getCubicBezierPoint(
      { x: 520, y: 95 },
      { x: 680, y: 65 },
      { x: 820, y: 125 },
      { x: 950, y: 95 },
      t
    );
  }
}

export const BlockClearanceMap: React.FC<BlockClearanceMapProps> = ({
  sectionTitle = 'Suburban Track Flow Telemetry',
  activeRake = {
    trainNumber: '#95401 FAST',
    speed: '92 km/h',
    signal: 'Sig Clear',
    headway: 'Headway 3m 40s',
  },
  stations = [],
}) => {
  const [trainProgress, setTrainProgress] = useState(30); // 5% to 95%
  const [selectedStation, setSelectedStation] = useState<StationTelemetry | null>(null);
  const [showRakeDetails, setShowRakeDetails] = useState(false);
  const [isScrubbing, setIsScrubbing] = useState(false);

  // Train auto movement
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

  const currentStations = stations.length > 0 ? stations : [
    { code: 'CSMT', name: 'CSMT Terminus', distanceKm: 0, platforms: [] },
    { code: 'DR', name: 'Dadar Central', distanceKm: 9, platforms: [] },
    { code: 'CLA', name: 'Kurla Jcn', distanceKm: 15, platforms: [] },
    { code: 'GC', name: 'Ghatkopar', distanceKm: 20, platforms: [] },
    { code: 'TNA', name: 'Thane', distanceKm: 34, platforms: [] },
  ];

  // Calculate dynamic station positions along the Bezier curve
  const stationNodes = useMemo(() => {
    const total = currentStations.length;
    return currentStations.map((st, idx) => {
      const tNorm = total > 1 ? idx / (total - 1) : 0.5;
      const { point } = evaluateTrackSpline(tNorm);
      const isTop = idx % 2 !== 0; // Alternate top / bottom
      return {
        ...st,
        x: point.x,
        y: point.y,
        isTop,
        labelX: point.x,
        labelY: isTop ? 22 : 148,
        guideY: isTop ? 40 : 134,
      };
    });
  }, [currentStations]);

  // Train current coordinate along spline
  const trainCoord = useMemo(() => {
    const normalized = Math.max(0, Math.min(1, (trainProgress - 5) / 90));
    return evaluateTrackSpline(normalized);
  }, [trainProgress]);

  // Compute synchronized real-time train journey leg
  const currentLeg = useMemo(() => {
    if (!currentStations || currentStations.length < 2) {
      return {
        statusText: 'Suburban Transit Tracking Active',
        subText: 'Real-time Signal Sync',
        isAtStation: false,
      };
    }
    const count = currentStations.length;
    const progressFrac = Math.max(0, Math.min(1, (trainProgress - 5) / 90));
    const segmentSize = 1 / (count - 1);
    const index = Math.min(count - 2, Math.floor(progressFrac / segmentSize));
    const localT = (progressFrac - index * segmentSize) / segmentSize;

    const currStn = currentStations[index];
    const nextStn = currentStations[index + 1];

    if (localT < 0.12) {
      return {
        statusText: `At ${currStn.name} [${currStn.code}]`,
        subText: currStn.departureTime ? `Dep ${currStn.departureTime}` : 'Boarding Active',
        isAtStation: true,
        currentStation: currStn,
        nextStation: nextStn,
      };
    } else if (localT > 0.88) {
      return {
        statusText: `Arriving at ${nextStn.name} [${nextStn.code}]`,
        subText: nextStn.arrivalTime ? `Platform Entry ${nextStn.arrivalTime}` : 'Arriving',
        isAtStation: true,
        currentStation: nextStn,
        nextStation: currentStations[index + 2] || null,
      };
    } else {
      return {
        statusText: `En route to ${nextStn.name} [${nextStn.code}]`,
        subText: nextStn.arrivalTime ? `ETA: ${nextStn.arrivalTime}` : 'In Transit',
        isAtStation: false,
        currentStation: currStn,
        nextStation: nextStn,
      };
    }
  }, [currentStations, trainProgress]);

  const originCode = currentStations[0]?.code || 'ORG';
  const originDepTime = currentStations[0]?.departureTime || '08:47 AM';
  const destinationCode = currentStations[currentStations.length - 1]?.code || 'DST';
  const destinationArrTime = currentStations[currentStations.length - 1]?.arrivalTime || '09:23 AM';

  return (
    <section className="w-full relative rounded-3xl bg-white/[0.02] backdrop-blur-2xl border border-glass-border p-4 sm:p-6 overflow-hidden">
      {/* Ambient Glows */}
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
          <span className="text-text-muted hidden md:inline">•</span>
          <span className="hidden md:inline font-mono text-[11px] text-primary font-medium">
            {currentLeg.statusText} ({currentLeg.subText})
          </span>
        </div>
        <div className="flex items-center gap-4 font-mono text-[11px] text-text-secondary">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-primary"></span> Signal Clear
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-secondary"></span> Caution Aspect
          </span>
          <span className="hidden md:flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-surface-container-highest"></span> Occupied Block
          </span>
        </div>
      </div>

      {/* SVG Canvas */}
      <div className="relative w-full py-2">
        <svg
          className="w-full h-44 sm:h-48 overflow-visible select-none"
          fill="none"
          viewBox="0 0 1000 190"
        >
          <defs>
            <linearGradient id="trackGlowGrad" x1="0%" x2="100%" y1="0%" y2="0%">
              <stop offset="0%" stopColor="#4edea3" stopOpacity="0.95" />
              <stop offset="40%" stopColor="#4edea3" stopOpacity="0.9" />
              <stop offset="55%" stopColor="#ffb95f" stopOpacity="0.85" />
              <stop offset="85%" stopColor="#4edea3" stopOpacity="0.95" />
              <stop offset="100%" stopColor="#3c4a42" stopOpacity="0.4" />
            </linearGradient>

            <filter id="neonTrackGlow" x="-20%" y="-30%" width="140%" height="160%">
              <feGaussianBlur stdDeviation="3.5" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>

            <radialGradient id="headlightBeam" cx="100%" cy="50%" r="90%">
              <stop offset="0%" stopColor="#ffffff" stopOpacity="0.9" />
              <stop offset="40%" stopColor="#4edea3" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#4edea3" stopOpacity="0" />
            </radialGradient>
          </defs>

          {/* 1. Underlying Rail Bed */}
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

          {/* 3. Active High-Voltage Lit Rail Line */}
          <path
            d="M 50 95 C 240 55, 340 135, 520 95 C 680 65, 820 125, 950 95"
            fill="none"
            filter="url(#neonTrackGlow)"
            stroke="url(#trackGlowGrad)"
            strokeWidth="3"
            strokeLinecap="round"
          />

          {/* Dynamic Station Nodes Rendered with Line-Specific Accuracy & Sequential Timings */}
          {stationNodes.map((node, i) => {
            const isFirst = i === 0;
            const isLast = i === stationNodes.length - 1;
            const anchor = isFirst ? 'start' : isLast ? 'end' : 'middle';

            const timeLabel = isFirst
              ? `Dep ${node.departureTime || '08:47 AM'}`
              : isLast
              ? `Arr ${node.arrivalTime || '09:23 AM'}`
              : `Arr ${node.arrivalTime || '--:--'} • Dep ${node.departureTime || '--:--'}`;

            return (
              <g
                key={`stn-${node.code}-${i}`}
                className="cursor-pointer group"
                onClick={() => setSelectedStation(node)}
              >
                {/* Guide Line */}
                <line
                  x1={node.x}
                  y1={node.y}
                  x2={node.x}
                  y2={node.guideY}
                  stroke="#4edea3"
                  strokeWidth="1"
                  strokeDasharray="2 2"
                  opacity="0.5"
                />

                {/* Node Circle */}
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={isFirst || isLast ? 7 : 6}
                  fill="#090A0C"
                  stroke={i === 2 ? '#ffb95f' : '#4edea3'}
                  strokeWidth="2.5"
                  className="group-hover:scale-125 transition-transform"
                />
                <circle cx={node.x} cy={node.y} r="2" fill={i === 2 ? '#ffb95f' : '#4edea3'} />

                {/* Station Name */}
                <text
                  x={node.labelX}
                  y={node.labelY}
                  textAnchor={anchor}
                  fill="#FFFFFF"
                  fontSize="11"
                  fontFamily="monospace"
                  fontWeight="600"
                >
                  {node.name}
                </text>

                {/* Code & Distance */}
                <text
                  x={node.labelX}
                  y={node.labelY + 11}
                  textAnchor={anchor}
                  fill={i === 2 ? '#ffb95f' : '#4edea3'}
                  fontSize="9"
                  fontFamily="monospace"
                >
                  {node.code} • {node.distanceKm.toFixed(1)} km
                </text>

                {/* Independent Station Scheduled Timing Badge */}
                <text
                  x={node.labelX}
                  y={node.isTop ? node.labelY - 11 : node.labelY + 22}
                  textAnchor={anchor}
                  fill={isFirst || isLast ? '#4edea3' : '#a1a7b4'}
                  fontSize="8.5"
                  fontFamily="monospace"
                  fontWeight="600"
                >
                  {timeLabel}
                </text>
              </g>
            );
          })}

          {/* Animated Mini EMU Train Rake */}
          <g
            transform={`translate(${trainCoord.point.x}, ${trainCoord.point.y}) rotate(${trainCoord.angle})`}
            className="cursor-pointer"
            onClick={() => setShowRakeDetails((prev) => !prev)}
          >
            {/* Headlight Beam Cone */}
            <polygon points="18,-1 52,-14 52,14 18,1" fill="url(#headlightBeam)" opacity="0.85" />

            {/* Rear Coach 3 */}
            <rect x="-38" y="-4.5" width="10" height="9" rx="1.5" fill="#1e2229" stroke="#4edea3" strokeWidth="0.8" />
            <rect x="-36" y="-2" width="2" height="4" fill="#4edea3" opacity="0.8" />
            <rect x="-32" y="-2" width="2" height="4" fill="#4edea3" opacity="0.8" />

            {/* Middle Motor Coach 2 with Pantograph */}
            <rect x="-26" y="-4.5" width="11" height="9" rx="1.5" fill="#1e2229" stroke="#4edea3" strokeWidth="0.8" />
            <line x1="-22" y1="-4.5" x2="-20.5" y2="-8" stroke="#ffb95f" strokeWidth="1" />
            <line x1="-20.5" y1="-8" x2="-19" y2="-4.5" stroke="#ffb95f" strokeWidth="1" />
            <line x1="-23" y1="-8" x2="-18" y2="-8" stroke="#ffffff" strokeWidth="1" />
            <rect x="-24" y="-2" width="2.5" height="4" fill="#4edea3" opacity="0.8" />
            <rect x="-19.5" y="-2" width="2.5" height="4" fill="#4edea3" opacity="0.8" />

            {/* Front Cab Coach 1 */}
            <path d="M -13 -4.5 L 14 -4.5 Q 18 -4.5 18 0 Q 18 4.5 14 4.5 L -13 4.5 Z" fill="#0d1117" stroke="#4edea3" strokeWidth="1.2" />
            <rect x="-11" y="2" width="25" height="1.8" fill="#4edea3" />
            <path d="M 8 -3 L 15 -3 Q 16.5 -3 16.5 0 Q 16.5 3 15 3 L 8 3 Z" fill="#38bdf8" opacity="0.9" />
            <circle cx="17.5" cy="-2.2" r="1.2" fill="#ffffff" filter="drop-shadow(0 0 4px #ffffff)" />
            <circle cx="17.5" cy="2.2" r="1.2" fill="#ffffff" filter="drop-shadow(0 0 4px #ffffff)" />
          </g>
        </svg>

        {/* Compact Floating Telemetry Badge Above Train with Live Synced Station State */}
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
                {currentLeg.statusText}
              </span>
              <span className="hidden sm:inline font-mono text-[9px] text-secondary font-medium">
                • {currentLeg.subText}
              </span>
            </div>

            {/* Extended Detail Inspection Card */}
            {showRakeDetails && (
              <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 p-3 rounded-2xl bg-surface-obsidian/98 border border-primary/60 shadow-2xl text-[11px] font-mono text-text-primary flex flex-col gap-1 z-40 whitespace-nowrap">
                <div className="flex items-center justify-between gap-3 pb-1 border-b border-white/[0.08]">
                  <span className="text-primary font-bold">{activeRake.trainNumber} LIVE INSPECTION</span>
                  <span className="text-text-muted text-[10px]">Headway: {activeRake.headway}</span>
                </div>
                <div className="text-[10px] text-text-secondary">
                  <span>Current Leg: <strong className="text-primary">{currentLeg.statusText}</strong></span>
                  <span className="mx-1.5">•</span>
                  <span>Timing: <strong className="text-secondary">{currentLeg.subText}</strong></span>
                </div>
                <div className="text-[10px] text-text-secondary">
                  <span>Speed: <strong className="text-primary">{activeRake.speed}</strong></span>
                  <span className="mx-1.5">•</span>
                  <span>Signal: <strong className="text-primary">{activeRake.signal}</strong></span>
                </div>
                <div className="text-[9px] text-text-muted">
                  Chainage: {originCode} → {destinationCode} • Automatic Interlock Active
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Dynamic Scrub Bar with Line-Specific Origin & Destination Timings */}
      <div className="mt-2 pt-3 border-t border-glass-border flex flex-col sm:flex-row items-center justify-between gap-3 font-mono text-[10px] text-text-muted">
        <div className="flex items-center gap-2">
          <span>Live Coordinate:</span>
          <span className="text-primary font-bold">{trainProgress.toFixed(1)}% along Corridor</span>
          <span className="text-text-muted">•</span>
          <span className="text-secondary font-medium">{currentLeg.statusText}</span>
          <span className="text-text-muted hidden lg:inline">• Speed: {activeRake.speed}</span>
        </div>

        <div className="flex items-center gap-3 w-full sm:w-80">
          <div className="flex flex-col text-left shrink-0">
            <span className="text-primary font-bold">{originCode}</span>
            <span className="text-[9px] text-text-muted">{originDepTime}</span>
          </div>
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
          <div className="flex flex-col text-right shrink-0">
            <span className="text-secondary font-bold">{destinationCode}</span>
            <span className="text-[9px] text-text-muted">{destinationArrTime}</span>
          </div>
        </div>

        <span className="text-text-secondary hidden md:inline">
          Click station nodes for live platform clearance
        </span>
      </div>

      {/* Station Clearance Drawer */}
      <StationInspectionDrawer
        isOpen={Boolean(selectedStation)}
        onClose={() => setSelectedStation(null)}
        station={selectedStation}
      />
    </section>
  );
};
