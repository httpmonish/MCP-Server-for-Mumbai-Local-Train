import React, { useMemo, useState } from "react";
import { useAuthStore } from "../store/useAuthStore";

interface RunningTrainProps {
  speed?: "normal" | "fast" | "slow";
}

export const RunningTrainBackground: React.FC<RunningTrainProps> = () => {
  const { selectedLine } = useAuthStore();
  const [videoOpacity, setVideoOpacity] = useState<number>(0.45);
  const [frameMode] = useState<boolean>(true);

  // Authentic Mumbai Suburban livery color palettes (Siemens / Bombardier rakes)
  const livery = useMemo(() => {
    switch (selectedLine) {
      case "WR":
        return {
          name: "Western Railway Siemens/Bombardier",
          baseBody: "from-slate-100 via-slate-50 to-slate-200",
          primaryStripe: "#1E3A8A", // Deep Navy/Purple
          secondaryStripe: "#F59E0B", // Safety Yellow
          accentPinstripe: "#0284C7", // Sky Cyan
          noseStripe: "#F59E0B",
          destLed: "VIRAR FAST",
          corridorTag: "WR • CHURCHGATE-VIRAR CORRIDOR",
        };
      case "HR":
        return {
          name: "Harbour Line Suburban Rake",
          baseBody: "from-slate-100 via-slate-50 to-slate-200",
          primaryStripe: "#065F46", // Dark Emerald
          secondaryStripe: "#FBBF24", // Yellow
          accentPinstripe: "#10B981", // Green
          noseStripe: "#F59E0B",
          destLed: "PANVEL SLOW",
          corridorTag: "HR • CSMT-VASHI-PANVEL CORRIDOR",
        };
      case "CR":
      default:
        return {
          name: "Central Railway Mumbai Local",
          baseBody: "from-slate-100 via-slate-50 to-slate-200",
          primaryStripe: "#7F1D1D", // Deep Central Maroon
          secondaryStripe: "#F59E0B", // Iconic Yellow
          accentPinstripe: "#DC2626", // Red
          noseStripe: "#F59E0B",
          destLed: "KASARA FAST",
          corridorTag: "CR • CSMT-KALYAN-KASARA CORRIDOR",
        };
    }
  }, [selectedLine]);

  return (
    <div
      className="fixed inset-0 pointer-events-none overflow-hidden z-0 select-none bg-slate-100/90"
      aria-hidden="true"
    >
      {/* 1. REAL MUMBAI LOCAL TRAIN VIDEO BACKGROUND LAYER */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <video
          autoPlay
          loop
          muted
          playsInline
          className="w-full h-full object-cover object-center filter saturate-[1.1] contrast-[1.05] transition-opacity duration-700"
          style={{ opacity: videoOpacity }}
        >
          <source src="/videos/mumbai_local_bg.mp4" type="video/mp4" />
        </video>

        {/* Light Grey Architectural Frosted Overlay (Ensures 100% text readability & executive contrast) */}
        <div className="absolute inset-0 bg-gradient-to-b from-slate-100/85 via-slate-50/75 to-slate-200/90 backdrop-blur-[1px]" />
      </div>

      {/* 2. MUMBAI LOCAL COACH WINDOW FRAME (Physical Frame Perspective) */}
      {frameMode && (
        <div className="absolute inset-2 sm:inset-4 rounded-3xl border-4 sm:border-8 border-slate-300/70 shadow-[inset_0_0_30px_rgba(100,116,139,0.25)] pointer-events-none z-1 flex flex-col justify-between p-3 sm:p-5">
          {/* Top Frame Header Bar */}
          <div className="flex justify-between items-center opacity-70">
            <div className="flex items-center gap-2 font-mono text-[9px] sm:text-[10px] text-slate-600 font-bold bg-white/80 backdrop-blur-xs px-2.5 py-1 rounded-md border border-slate-300 pointer-events-auto shadow-2xs">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>MUMBAI LOCAL EMU // CABIN VIEWPORT</span>
              <button
                type="button"
                onClick={() => setVideoOpacity((prev) => (prev > 0.6 ? 0.35 : 0.75))}
                className="ml-2 px-2 py-0.5 rounded bg-slate-100 hover:bg-slate-200 text-slate-800 text-[9px] font-mono font-bold transition-all border border-slate-300 cursor-pointer shadow-2xs active:scale-95"
                title="Toggle Real Train Video Vibrancy"
              >
                🎥 Video: {videoOpacity > 0.6 ? "Vivid" : "Soft Focus"}
              </button>
            </div>

            <div className="font-hand text-xs sm:text-sm text-slate-600 font-bold bg-white/60 backdrop-blur-xs px-2.5 py-0.5 rounded-md border border-slate-300/80">
              {livery.corridorTag} ✍️
            </div>
          </div>

          {/* Center Window Guard Rail Bars (Classic Mumbai Local Iron Grills) */}
          <div className="w-full flex flex-col gap-8 opacity-15">
            <div className="w-full h-[1px] bg-slate-700 shadow-xs" />
            <div className="w-full h-[1px] bg-slate-700 shadow-xs" />
          </div>

          {/* Bottom Frame Stamp */}
          <div className="flex justify-between items-center opacity-60">
            <div className="font-mono text-[9px] text-slate-500 bg-white/60 px-2 py-0.5 rounded border border-slate-300/60">
              ROLLING STOCK: BMR-110 // TRACTION LIVE
            </div>
            <div className="font-mono text-[9px] text-slate-500 bg-white/60 px-2 py-0.5 rounded border border-slate-300/60">
              GPS LAT/LONG: 19.0760° N, 72.8777° E
            </div>
          </div>
        </div>
      )}

      {/* 3. Static Moiré Interference Pattern (Dual 45° vs 48.5° optical gratings) */}
      <div
        className="absolute inset-0 opacity-[0.04] pointer-events-none"
        style={{
          backgroundImage: `
            repeating-linear-gradient(45deg, #64748b 0, #64748b 1px, transparent 0, transparent 14px),
            repeating-linear-gradient(48.5deg, #475569 0, #475569 1px, transparent 0, transparent 14px)
          `,
        }}
      />

      {/* 4. Dynamic Ambient Moiré Drift Mesh */}
      <div
        className="absolute inset-0 opacity-[0.03] animate-moire-drift pointer-events-none"
        style={{
          backgroundImage: `
            repeating-linear-gradient(135deg, #0284c7 0, #0284c7 1.5px, transparent 0, transparent 24px),
            repeating-linear-gradient(137.5deg, #6366f1 0, #6366f1 1.5px, transparent 0, transparent 24px)
          `,
          backgroundSize: "200% 200%",
        }}
      />

      {/* 5. Fine Blueprint Grid Mesh */}
      <svg className="absolute inset-0 w-full h-full opacity-30 pointer-events-none" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="bg-grid-mesh" width="80" height="80" patternUnits="userSpaceOnUse">
            <path d="M 80 0 L 0 0 0 80" fill="none" stroke="rgba(148, 163, 184, 0.16)" strokeWidth="0.75" />
            <path d="M 40 0 L 40 80 M 0 40 L 80 40" fill="none" stroke="rgba(148, 163, 184, 0.08)" strokeWidth="0.5" strokeDasharray="2 3" />
            <circle cx="80" cy="0" r="1.5" fill="rgba(100, 116, 139, 0.2)" />
            <circle cx="0" cy="80" r="1.5" fill="rgba(100, 116, 139, 0.2)" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#bg-grid-mesh)" />
      </svg>

      {/* 6. RAILWAY CORRIDOR INFRASTRUCTURE (Catenary, Masts, Rails, Sleepers) */}
      <div className="absolute bottom-0 left-0 right-0 h-32 pointer-events-none">
        {/* Overhead 25 kV AC Catenary & Contact Wire */}
        <div className="absolute top-2 left-0 right-0 h-[1.5px] bg-slate-400/60" />
        <div className="absolute top-8 left-0 right-0 h-[1.5px] bg-amber-700/50 shadow-xs" />

        {/* Dropper Wires */}
        <div className="absolute top-2 left-0 right-0 h-6 flex justify-between px-3 opacity-30">
          {Array.from({ length: 40 }).map((_, i) => (
            <div key={i} className="w-[1px] h-full bg-slate-500" />
          ))}
        </div>

        {/* OHE Steel Lattice Masts */}
        <div className="absolute top-0 left-0 right-0 h-28 flex justify-between px-12 opacity-35">
          {Array.from({ length: 7 }).map((_, i) => (
            <div key={i} className="flex flex-col items-center">
              <div className="w-10 h-2.5 border-t-2 border-slate-600 -mt-1" />
              <div className="w-3 h-24 border-l border-r border-slate-600 relative">
                <div className="absolute inset-0 flex flex-col justify-between py-1 opacity-50">
                  <div className="w-full h-[1px] bg-slate-600" />
                  <div className="w-full h-[1px] bg-slate-600 rotate-45" />
                  <div className="w-full h-[1px] bg-slate-600" />
                  <div className="w-full h-[1px] bg-slate-600 -rotate-45" />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* 3-Aspect Signal Aspect */}
        <div className="absolute top-4 right-36 flex flex-col items-center opacity-65">
          <div className="w-3.5 h-8 rounded-md bg-slate-900 p-0.5 flex flex-col justify-between items-center shadow-md border border-slate-700">
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_10px_#34D399]" />
            <div className="w-2 h-2 rounded-full bg-slate-800" />
            <div className="w-2 h-2 rounded-full bg-slate-800" />
          </div>
          <div className="w-1.5 h-16 bg-slate-700" />
        </div>

        {/* Concrete Viaduct Deck & Ballast Bed */}
        <div className="absolute bottom-0 left-0 right-0 h-14 bg-gradient-to-b from-slate-300 via-slate-400/80 to-slate-500 border-t-2 border-slate-400 shadow-inner" />

        {/* Pre-stressed Concrete Sleepers */}
        <div className="absolute bottom-6 left-0 right-0 h-6 flex justify-between px-1 opacity-55">
          {Array.from({ length: 90 }).map((_, i) => (
            <div key={i} className="w-2 h-full bg-slate-700 rounded-xs shadow-xs" />
          ))}
        </div>

        {/* Double Running Rails with Steel Head Gleam */}
        <div className="absolute bottom-11 left-0 right-0 h-1.5 bg-gradient-to-b from-slate-200 via-slate-500 to-slate-800 shadow-[0_1px_3px_rgba(0,0,0,0.4)]" />
        <div className="absolute bottom-7 left-0 right-0 h-1.5 bg-gradient-to-b from-slate-200 via-slate-500 to-slate-800 shadow-[0_1px_3px_rgba(0,0,0,0.4)]" />
      </div>

      {/* 7. DYNAMIC TRAVERSING RUNNING TRAIN OVER THE VIDEO */}
      <div className="absolute bottom-9 left-0 w-full overflow-visible pointer-events-none animate-train-traverse">
        <div className="inline-flex items-end relative filter drop-shadow-lg">
          {/* Forward High-Beam projection */}
          <div className="absolute -right-48 bottom-3 w-64 h-16 bg-gradient-to-r from-amber-300/40 via-amber-200/20 to-transparent transform -skew-x-12 blur-xs pointer-events-none" />

          {/* Coach 1: Trailing Cab */}
          <RealMumbaiEmuCoach
            coachType="cab"
            isLeading={false}
            hasPantograph={false}
            livery={livery}
            coachNumber="9401"
          />

          {/* Coach 2: Standard Second Class Coach */}
          <RealMumbaiEmuCoach
            coachType="trailer"
            isLeading={false}
            hasPantograph={false}
            livery={livery}
            coachNumber="9402"
          />

          {/* Coach 3: Motor Coach with Diamond Pantograph & Arcing Sparks */}
          <RealMumbaiEmuCoach
            coachType="motor"
            isLeading={false}
            hasPantograph={true}
            livery={livery}
            coachNumber="9403"
          />

          {/* Coach 4: Ladies / First Class Coach */}
          <RealMumbaiEmuCoach
            coachType="trailer"
            isLeading={false}
            hasPantograph={false}
            livery={livery}
            coachNumber="9404"
          />

          {/* Coach 5: Leading Driver Cab (Distinctive Curved Nose) */}
          <RealMumbaiEmuCoach
            coachType="cab"
            isLeading={true}
            hasPantograph={false}
            livery={livery}
            coachNumber="9405"
            destinationText={livery.destLed}
          />
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// REALISTIC MUMBAI LOCAL EMU COACH COMPONENT
// ============================================================================
interface RealCoachProps {
  coachType: "cab" | "trailer" | "motor";
  isLeading: boolean;
  hasPantograph: boolean;
  livery: {
    baseBody: string;
    primaryStripe: string;
    secondaryStripe: string;
    accentPinstripe: string;
    noseStripe: string;
  };
  coachNumber: string;
  destinationText?: string;
}

const RealMumbaiEmuCoach: React.FC<RealCoachProps> = ({
  coachType,
  isLeading,
  hasPantograph,
  livery,
  coachNumber,
  destinationText,
}) => {
  const isCab = coachType === "cab";

  return (
    <div className="relative flex flex-col items-center">
      {/* Roof & Pantograph */}
      <div className="w-full h-7 relative flex justify-center items-end">
        {hasPantograph && (
          <div className="w-20 h-7 relative flex flex-col items-center justify-end -mb-0.5">
            <div className="w-14 h-1 bg-slate-900 relative rounded-full">
              <div className="absolute -top-1.5 left-5 w-3 h-3 rounded-full bg-cyan-300 animate-spark opacity-90 blur-xs" />
              <div className="absolute -top-1 left-9 w-2 h-2 rounded-full bg-white animate-pulse" />
            </div>
            <div className="w-8 h-5 border-t-2 border-l border-r border-slate-800 -rotate-12 transform origin-bottom scale-y-110" />
            <div className="w-12 h-1.5 flex justify-between px-1">
              <div className="w-1.5 h-1.5 rounded-full bg-amber-600 border border-slate-800" />
              <div className="w-1.5 h-1.5 rounded-full bg-amber-600 border border-slate-800" />
              <div className="w-1.5 h-1.5 rounded-full bg-amber-600 border border-slate-800" />
            </div>
          </div>
        )}

        {!hasPantograph && (
          <div className="w-3/4 h-2 flex justify-around px-2 mb-0.5">
            <div className="w-8 h-1.5 bg-slate-400 rounded-t-sm border-t border-slate-500" />
            <div className="w-8 h-1.5 bg-slate-400 rounded-t-sm border-t border-slate-500" />
            <div className="w-8 h-1.5 bg-slate-400 rounded-t-sm border-t border-slate-500" />
          </div>
        )}
      </div>

      {/* Main Coach Body */}
      <div
        className={`h-14 ${
          isCab ? "w-48" : "w-44"
        } bg-gradient-to-b ${livery.baseBody} border-t-2 border-b border-slate-500 relative flex flex-col justify-between overflow-hidden shadow-md ${
          isCab && isLeading
            ? "rounded-r-3xl border-r-2 border-slate-600"
            : isCab && !isLeading
            ? "rounded-l-2xl border-l-2 border-slate-600"
            : "rounded-none"
        }`}
      >
        <div className="w-full h-1.5 bg-slate-300/90 border-b border-slate-400/60 flex justify-between px-1">
          <div className="w-full h-0.5 bg-slate-400/40 mt-0.5" />
        </div>

        <div className="w-full h-1" style={{ backgroundColor: livery.secondaryStripe }} />

        {/* Windows & Doors */}
        <div className="flex items-center justify-between px-2 py-0.5">
          {isCab && !isLeading && (
            <div className="w-4 h-6 bg-slate-800 rounded-l-md border border-slate-600 shadow-inner flex items-center justify-center">
              <div className="w-1 h-3 bg-red-600 rounded-xs shadow-[0_0_5px_#DC2626]" />
            </div>
          )}

          {/* Mumbai Local Doorway 1 */}
          <div className="w-5 h-8 bg-slate-900 rounded-xs border border-slate-700 relative overflow-hidden flex items-center justify-center">
            <div className="w-0.5 h-full bg-slate-300 z-10" />
            <div className="absolute bottom-0 left-0.5 w-2 h-5 bg-slate-700/80 rounded-t-xs" />
          </div>

          {/* Passenger Windows */}
          <div className="flex gap-1.5">
            <div className="w-6 h-5 bg-amber-100/90 border border-slate-500 rounded-xs shadow-inner relative overflow-hidden flex flex-col justify-center">
              <div className="w-full h-[0.5px] bg-slate-600/60 my-0.5" />
              <div className="w-full h-[0.5px] bg-slate-600/60" />
              <div className="absolute top-1 left-2 w-2 h-2.5 bg-slate-700/50 rounded-full" />
            </div>

            <div className="w-6 h-5 bg-amber-100/90 border border-slate-500 rounded-xs shadow-inner relative overflow-hidden flex flex-col justify-center">
              <div className="w-full h-[0.5px] bg-slate-600/60 my-0.5" />
              <div className="w-full h-[0.5px] bg-slate-600/60" />
              <div className="absolute top-1 left-2.5 w-2 h-2.5 bg-slate-700/50 rounded-full" />
            </div>

            <div className="w-6 h-5 bg-amber-100/90 border border-slate-500 rounded-xs shadow-inner relative overflow-hidden flex flex-col justify-center">
              <div className="w-full h-[0.5px] bg-slate-600/60 my-0.5" />
              <div className="w-full h-[0.5px] bg-slate-600/60" />
            </div>
          </div>

          {/* Mumbai Local Doorway 2 */}
          <div className="w-5 h-8 bg-slate-900 rounded-xs border border-slate-700 relative overflow-hidden flex items-center justify-center">
            <div className="w-0.5 h-full bg-slate-300 z-10" />
            <div className="absolute bottom-0 right-0.5 w-2 h-5 bg-slate-700/80 rounded-t-xs" />
          </div>

          {/* Leading Driver Cab */}
          {isCab && isLeading && (
            <div className="flex flex-col items-end gap-0.5 mr-0.5">
              {destinationText && (
                <div className="bg-black text-amber-400 font-mono text-[6px] px-1.5 py-0.2 rounded-xs tracking-tighter uppercase font-black shadow-xs border border-amber-500/40">
                  {destinationText}
                </div>
              )}

              <div className="w-8 h-6 bg-gradient-to-r from-slate-900 to-sky-950 rounded-r-2xl border-2 border-slate-600 shadow-inner flex items-center justify-between px-1 relative">
                <div className="w-2.5 h-0.5 bg-slate-400 rotate-45 transform origin-left" />
                <div className="flex flex-col gap-0.5">
                  <div className="w-2 h-2 rounded-full bg-amber-200 shadow-[0_0_8px_#FEF08A] border border-amber-300 animate-pulse" />
                  <div className="w-2 h-2 rounded-full bg-amber-200 shadow-[0_0_8px_#FEF08A] border border-amber-300 animate-pulse" />
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="w-full h-0.5" style={{ backgroundColor: livery.accentPinstripe }} />

        {/* Lower Racing Stripe */}
        <div
          className="w-full h-3 flex items-center justify-between px-2.5 relative"
          style={{ backgroundColor: livery.primaryStripe }}
        >
          <span className="font-mono text-[7px] text-white font-black uppercase tracking-widest">
            {coachNumber}
          </span>
          {isCab && isLeading && (
            <div
              className="absolute right-0 top-0 bottom-0 w-4 rounded-r-3xl"
              style={{ backgroundColor: livery.noseStripe }}
            />
          )}
          <span className="font-mono text-[6px] text-amber-300 font-bold uppercase tracking-wider">
            CR-SUBURBAN
          </span>
        </div>
      </div>

      {/* Undercarriage Bogies */}
      <div className="w-full flex justify-around px-4 -mt-1">
        <div className="flex items-center gap-2 bg-slate-900/90 px-1 py-0.5 rounded-sm border border-slate-700">
          <div className="w-3.5 h-3.5 rounded-full bg-slate-800 border-2 border-slate-500 flex items-center justify-center animate-spin">
            <div className="w-1 h-1 rounded-full bg-slate-400" />
          </div>
          <div className="w-2 h-1 bg-amber-700 rounded-xs" />
          <div className="w-3.5 h-3.5 rounded-full bg-slate-800 border-2 border-slate-500 flex items-center justify-center animate-spin">
            <div className="w-1 h-1 rounded-full bg-slate-400" />
          </div>
        </div>

        <div className="flex items-center gap-2 bg-slate-900/90 px-1 py-0.5 rounded-sm border border-slate-700">
          <div className="w-3.5 h-3.5 rounded-full bg-slate-800 border-2 border-slate-500 flex items-center justify-center animate-spin">
            <div className="w-1 h-1 rounded-full bg-slate-400" />
          </div>
          <div className="w-2 h-1 bg-amber-700 rounded-xs" />
          <div className="w-3.5 h-3.5 rounded-full bg-slate-800 border-2 border-slate-500 flex items-center justify-center animate-spin">
            <div className="w-1 h-1 rounded-full bg-slate-400" />
          </div>
        </div>
      </div>
    </div>
  );
};
