import React, { useMemo } from "react";
import { useAuthStore } from "../store/useAuthStore";

interface RunningTrainProps {
  speed?: "normal" | "fast" | "slow";
}

export const RunningTrainBackground: React.FC<RunningTrainProps> = () => {
  const { selectedLine } = useAuthStore();

  // Livery themes matching line corridors
  const livery = useMemo(() => {
    switch (selectedLine) {
      case "WR":
        return {
          stripe: "#2563EB",
          stripeDark: "#1D4ED8",
          accent: "#38BDF8",
          tag: "WR • CHURCHGATE-VIRAR",
          destBoard: "VIRAR FAST",
          hornFreq: "440 Hz",
          oheVoltage: "25 kV AC 50Hz",
        };
      case "HR":
        return {
          stripe: "#059669",
          stripeDark: "#047857",
          accent: "#34D399",
          tag: "HR • CSMT-PANVEL",
          destBoard: "PANVEL LOCAL",
          hornFreq: "420 Hz",
          oheVoltage: "25 kV AC 50Hz",
        };
      case "CR":
      default:
        return {
          stripe: "#DC2626",
          stripeDark: "#B91C1C",
          accent: "#F87171",
          tag: "CR • CSMT-KASARA",
          destBoard: "KASARA FAST",
          hornFreq: "450 Hz",
          oheVoltage: "25 kV AC 50Hz",
        };
    }
  }, [selectedLine]);

  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0 select-none">
      {/* 1. Base Atmospheric Light Grey Canvas */}
      <div className="absolute inset-0 bg-gradient-to-b from-slate-100 via-slate-200/70 to-slate-300/40" />

      {/* 2. Static Moiré Interference Layer: Dual angled linear gratings with 3.2° phase delta */}
      <div
        className="absolute inset-0 opacity-40 mix-blend-multiply"
        style={{
          backgroundImage: `
            repeating-linear-gradient(45deg, rgba(148, 163, 184, 0.07) 0px, rgba(148, 163, 184, 0.07) 1px, transparent 1px, transparent 14px),
            repeating-linear-gradient(48.5deg, rgba(100, 116, 139, 0.07) 0px, rgba(100, 116, 139, 0.07) 1px, transparent 1px, transparent 14px),
            radial-gradient(circle at 50% 50%, rgba(203, 213, 225, 0.4) 0%, transparent 80%)
          `,
        }}
      />

      {/* 3. Dynamic Moiré Wave Animation: Drifting optical mesh creating alive interference patterns */}
      <div
        className="absolute inset-0 opacity-25 animate-moire-drift pointer-events-none"
        style={{
          backgroundImage: `
            repeating-linear-gradient(135deg, rgba(99, 102, 241, 0.04) 0px, rgba(99, 102, 241, 0.04) 1px, transparent 1px, transparent 18px),
            repeating-linear-gradient(137.5deg, rgba(244, 63, 94, 0.03) 0px, rgba(244, 63, 94, 0.03) 1px, transparent 1px, transparent 18px)
          `,
          backgroundSize: "200% 200%",
        }}
      />

      {/* 4. Precision Blueprint Grid Lines with Micro Crosshairs */}
      <svg className="absolute inset-0 w-full h-full opacity-35" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="blueprint-grid" width="80" height="80" patternUnits="userSpaceOnUse">
            <path d="M 80 0 L 0 0 0 80" fill="none" stroke="rgba(148, 163, 184, 0.22)" strokeWidth="0.75" />
            <path d="M 40 0 L 40 80 M 0 40 L 80 40" fill="none" stroke="rgba(148, 163, 184, 0.12)" strokeWidth="0.5" strokeDasharray="2 3" />
            <circle cx="80" cy="0" r="1.5" fill="rgba(100, 116, 139, 0.3)" />
            <circle cx="0" cy="80" r="1.5" fill="rgba(100, 116, 139, 0.3)" />
            <path d="M 37 40 L 43 40 M 40 37 L 40 43" stroke="rgba(99, 102, 241, 0.25)" strokeWidth="0.75" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#blueprint-grid)" />
      </svg>

      {/* 5. Handwritten Blueprint Annotations, Technical Stamps & Notes (Static Structure) */}
      <div className="absolute inset-0 pointer-events-none text-slate-500/80">
        {/* Top-left engineering stamp */}
        <div className="absolute top-20 left-8 hidden lg:block -rotate-2 transform">
          <div className="border border-slate-400/50 bg-white/40 backdrop-blur-xs px-3 py-1.5 rounded shadow-xs">
            <div className="font-mono text-[9px] uppercase tracking-widest text-slate-400 font-bold">
              SURVEY SPECIFICATION // CR-2026
            </div>
            <div className="font-blueprint text-sm text-slate-700 font-semibold tracking-wide">
              Central Railway Northeast Corridor (Kasara Ghats)
            </div>
            <div className="font-hand text-xs text-rose-600/90 font-bold -mt-0.5">
              1 in 37 Gradient • 120.8 km from CSMT Terminus ✍️
            </div>
          </div>
        </div>

        {/* Top-right technical note with sketch arrow */}
        <div className="absolute top-24 right-12 hidden xl:block rotate-1 transform">
          <div className="font-hand text-base text-indigo-700/80 font-bold leading-tight max-w-[220px]">
            &ldquo;Timetable synchronized with today's m-Indicator master run sheet&rdquo;
            <span className="block text-[11px] font-mono text-slate-400 font-normal mt-0.5">
              Ref: OHE 25kV • 110 km/h Rake
            </span>
          </div>
          <svg className="w-16 h-8 text-indigo-400/60 ml-12" viewBox="0 0 64 32" fill="none">
            <path d="M 4 8 C 24 6, 44 18, 56 26" stroke="currentColor" strokeWidth="1.5" strokeDasharray="3 2" />
            <path d="M 50 26 L 56 26 L 54 20" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        </div>

        {/* Bottom-left track engineering coordinates */}
        <div className="absolute bottom-28 left-8 hidden md:block rotate-1">
          <div className="font-mono text-[10px] text-slate-400/80 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500/70 inline-block animate-pulse" />
            <span>TRACK CIRCUIT: TLA-KSRA SECTION 100% HEALTHY</span>
            <span className="font-hand text-sm text-slate-600 font-bold">✓ Clear block</span>
          </div>
        </div>

        {/* Bottom-right stamped badge */}
        <div className="absolute bottom-24 right-8 hidden lg:block -rotate-3">
          <div className="border-2 border-dashed border-slate-400/40 rounded-lg p-2 bg-slate-100/40 backdrop-blur-xs text-right">
            <div className="font-mono text-[8px] tracking-widest uppercase text-slate-400">
              COMMUTE ENGINE VERIFIED
            </div>
            <div className="font-blueprint text-xs text-slate-600 font-bold">
              AUTONOMOUS SPEED MATRIX: ACTIVE
            </div>
          </div>
        </div>
      </div>

      {/* 6. Distant Horizon: Silhouette Western Ghats / Mumbai Skyline */}
      <div className="absolute bottom-20 left-0 right-0 h-32 opacity-15 pointer-events-none">
        <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="w-full h-full text-slate-600 fill-current">
          {/* Subtle rolling Sahyadri hills & Kasara Ghats ridge */}
          <path d="M 0 120 L 0 75 Q 80 40, 160 65 T 320 50 T 480 80 T 640 45 T 800 65 T 960 40 T 1120 70 T 1200 60 L 1200 120 Z" />
          {/* Faint distant transmission pylons & city silhouettes */}
          <rect x="220" y="35" width="2" height="30" />
          <path d="M 215 45 L 225 45 M 216 55 L 224 55" stroke="currentColor" strokeWidth="1.5" />
          <rect x="740" y="25" width="2" height="40" />
          <path d="M 735 35 L 745 35 M 736 48 L 744 48" stroke="currentColor" strokeWidth="1.5" />
        </svg>
      </div>

      {/* 7. Railway Infrastructure Layer: Tracks, Overhead Electrification (OHE) Masts & Catenary */}
      <div className="absolute bottom-0 left-0 right-0 h-28 pointer-events-none">
        {/* Overhead Catenary Wire spanning across screen */}
        <div className="absolute top-2 left-0 right-0 h-[1.5px] bg-slate-400/50 shadow-xs" />
        <div className="absolute top-7 left-0 right-0 h-[1px] bg-slate-500/40" />

        {/* Droppers (vertical wire supports connecting contact wire to catenary) */}
        <div className="absolute top-2 left-0 right-0 h-5 flex justify-between px-2 opacity-30">
          {Array.from({ length: 30 }).map((_, i) => (
            <div key={i} className="w-[1px] h-full bg-slate-500" />
          ))}
        </div>

        {/* OHE Lattice Steel Masts repeating across */}
        <div className="absolute top-0 left-0 right-0 h-24 flex justify-between px-10 opacity-40">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="flex flex-col items-center">
              <div className="w-8 h-2 border-t-2 border-slate-500 -mt-1" />
              <div className="w-2.5 h-20 border-l border-r border-slate-500 relative">
                {/* Internal cross bracing */}
                <div className="absolute inset-0 flex flex-col justify-between py-1 opacity-60">
                  <div className="w-full h-[1px] bg-slate-500" />
                  <div className="w-full h-[1px] bg-slate-500 rotate-45" />
                  <div className="w-full h-[1px] bg-slate-500" />
                  <div className="w-full h-[1px] bg-slate-500 -rotate-45" />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Signal Aspect Gantry on right */}
        <div className="absolute top-4 right-28 flex flex-col items-center opacity-60">
          <div className="w-3 h-7 rounded-sm bg-slate-800 p-0.5 flex flex-col justify-between items-center shadow-xs">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_#10B981]" />
            <div className="w-1.5 h-1.5 rounded-full bg-slate-700" />
            <div className="w-1.5 h-1.5 rounded-full bg-slate-700" />
          </div>
          <div className="w-1 h-14 bg-slate-700" />
        </div>

        {/* Concrete Viaduct Pier & Trackbed */}
        <div className="absolute bottom-6 left-0 right-0 h-8 bg-gradient-to-b from-slate-300 to-slate-400/80 border-t-2 border-slate-400 shadow-inner" />

        {/* Dual Steel Rails */}
        <div className="absolute bottom-11 left-0 right-0 h-1 bg-slate-600/90 shadow-[0_1px_2px_rgba(0,0,0,0.2)]" />
        <div className="absolute bottom-8 left-0 right-0 h-1 bg-slate-600/90 shadow-[0_1px_2px_rgba(0,0,0,0.2)]" />

        {/* Concrete Sleepers under tracks */}
        <div className="absolute bottom-7 left-0 right-0 h-6 flex justify-between px-1 opacity-45">
          {Array.from({ length: 80 }).map((_, i) => (
            <div key={i} className="w-1.5 h-full bg-slate-700 rounded-xs shadow-xs" />
          ))}
        </div>

        {/* Ballast Stone Texture */}
        <div className="absolute bottom-0 left-0 right-0 h-7 bg-slate-400/60 border-t border-slate-400" />
      </div>

      {/* 8. DYNAMIC RUNNING TRAIN ANIMATION */}
      {/* Train moves smoothly from Left to Right in a continuous 16-second loop */}
      <div className="absolute bottom-10 left-0 w-full overflow-visible pointer-events-none animate-train-traverse">
        <div className="inline-flex items-end relative filter drop-shadow-md">
          {/* Headlamp Forward Beam projection */}
          <div className="absolute -right-36 bottom-2 w-48 h-12 bg-gradient-to-r from-amber-200/50 via-amber-100/20 to-transparent transform -skew-x-12 blur-xs pointer-events-none" />

          {/* Coach 1: Rear Cab / Trailing Coach */}
          <EmuCoach
            isCab={true}
            isLeading={false}
            hasPantograph={false}
            liveryColor={livery.stripe}
            accentColor={livery.accent}
            coachCode="CAB-401"
          />

          {/* Coach 2: Standard Passenger Trailer */}
          <EmuCoach
            isCab={false}
            isLeading={false}
            hasPantograph={false}
            liveryColor={livery.stripe}
            accentColor={livery.accent}
            coachCode="TC-402"
          />

          {/* Coach 3: Motor Coach with Active Pantograph */}
          <EmuCoach
            isCab={false}
            isLeading={false}
            hasPantograph={true}
            liveryColor={livery.stripe}
            accentColor={livery.accent}
            coachCode="MC-403"
          />

          {/* Coach 4: Standard Passenger Trailer */}
          <EmuCoach
            isCab={false}
            isLeading={false}
            hasPantograph={false}
            liveryColor={livery.stripe}
            accentColor={livery.accent}
            coachCode="TC-404"
          />

          {/* Coach 5: Leading Motor Cab Coach with Windshield & Destination Board */}
          <EmuCoach
            isCab={true}
            isLeading={true}
            hasPantograph={false}
            liveryColor={livery.stripe}
            accentColor={livery.accent}
            coachCode="CAB-405"
            destBoard={livery.destBoard}
          />
        </div>
      </div>
    </div>
  );
};

interface EmuCoachProps {
  isCab: boolean;
  isLeading: boolean;
  hasPantograph: boolean;
  liveryColor: string;
  accentColor: string;
  coachCode: string;
  destBoard?: string;
}

const EmuCoach: React.FC<EmuCoachProps> = ({
  isCab,
  isLeading,
  hasPantograph,
  liveryColor,
  accentColor,
  coachCode,
  destBoard,
}) => {
  return (
    <div className="relative flex flex-col items-center">
      {/* Pantograph (for Motor Coach) */}
      {hasPantograph && (
        <div className="w-16 h-6 relative -mb-0.5 flex flex-col items-center">
          {/* Top contact strip sliding under catenary */}
          <div className="w-10 h-0.5 bg-slate-800 relative">
            {/* Pantograph Electric Spark Effect */}
            <div className="absolute -top-1 left-4 w-2 h-2 rounded-full bg-cyan-300 animate-spark opacity-80 blur-xs" />
          </div>
          {/* Diamond scissor frame */}
          <div className="w-6 h-5 border-t border-l border-r border-slate-700 -rotate-12 transform origin-bottom scale-y-110" />
          <div className="w-8 h-1 bg-slate-800 rounded-sm" />
        </div>
      )}

      {/* Main Coach Body */}
      <div
        className={`h-11 ${
          isCab ? "w-44" : "w-40"
        } bg-gradient-to-b from-slate-200 via-slate-100 to-slate-300 border-t border-b border-slate-400 relative flex flex-col justify-between overflow-hidden shadow-sm ${
          isCab && isLeading ? "rounded-r-2xl" : isCab && !isLeading ? "rounded-l-2xl" : "rounded-none"
        }`}
      >
        {/* Upper Roof Ribs */}
        <div className="w-full h-1 bg-slate-300/80 border-b border-slate-400/40 flex justify-around">
          <div className="w-6 h-full bg-slate-400/40" />
          <div className="w-6 h-full bg-slate-400/40" />
          <div className="w-6 h-full bg-slate-400/40" />
        </div>

        {/* Windows & Doors Row */}
        <div className="flex items-center justify-between px-2 py-0.5">
          {isCab && !isLeading && (
            <div className="w-3.5 h-5 bg-cyan-900/80 rounded-l-md border border-slate-600 shadow-inner" />
          )}

          {/* Door 1 */}
          <div className="w-3.5 h-7 bg-slate-800/85 rounded-xs border border-slate-600 flex flex-col justify-center items-center">
            <div className="w-1 h-3 bg-amber-100/90 rounded-xs" />
          </div>

          {/* Windows Cluster (Passenger compartment with warm interior light) */}
          <div className="flex gap-1.5">
            <div className="w-5 h-4 bg-amber-100/85 border border-slate-500 rounded-xs shadow-inner relative overflow-hidden">
              <div className="absolute top-1 left-1 w-1.5 h-2 bg-slate-700/40 rounded-full" />
            </div>
            <div className="w-5 h-4 bg-amber-100/85 border border-slate-500 rounded-xs shadow-inner relative overflow-hidden">
              <div className="absolute top-1 left-2 w-1.5 h-2 bg-slate-700/40 rounded-full" />
            </div>
            <div className="w-5 h-4 bg-amber-100/85 border border-slate-500 rounded-xs shadow-inner" />
          </div>

          {/* Door 2 */}
          <div className="w-3.5 h-7 bg-slate-800/85 rounded-xs border border-slate-600 flex flex-col justify-center items-center">
            <div className="w-1 h-3 bg-amber-100/90 rounded-xs" />
          </div>

          {/* Leading Cab Windshield & Destination LED Header */}
          {isCab && isLeading && (
            <div className="flex flex-col items-end gap-0.5 mr-0.5">
              {destBoard && (
                <div className="bg-slate-950 text-amber-400 font-mono text-[6px] px-1 py-0.2 rounded-xs tracking-tighter uppercase font-bold">
                  {destBoard}
                </div>
              )}
              <div className="w-6 h-5 bg-gradient-to-r from-cyan-900 to-sky-700 rounded-r-xl border border-slate-600 shadow-inner flex items-center justify-end pr-0.5">
                {/* Twin High-Intensity LED Headlights */}
                <div className="w-1.5 h-1.5 rounded-full bg-amber-200 shadow-[0_0_6px_#FEF08A] border border-amber-300 animate-pulse" />
              </div>
            </div>
          )}
        </div>

        {/* Accent Pinstripe */}
        <div className="w-full h-0.5" style={{ backgroundColor: accentColor }} />

        {/* Lower Livery Racing Stripe (Central Red / Western Blue / Harbour Green) */}
        <div
          className="w-full h-2 flex items-center justify-between px-2"
          style={{ backgroundColor: liveryColor }}
        >
          <span className="font-mono text-[6px] text-white/90 font-bold uppercase tracking-widest">
            {coachCode}
          </span>
          <div className="w-8 h-0.5 bg-white/60" />
        </div>
      </div>

      {/* Undercarriage Bogies & Wheels */}
      <div className="w-full flex justify-around px-3 -mt-0.5">
        {/* Bogie 1 */}
        <div className="flex items-center gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-slate-800 border border-slate-600 flex items-center justify-center animate-spin">
            <div className="w-1 h-1 rounded-full bg-slate-400" />
          </div>
          <div className="w-2 h-0.5 bg-slate-700" />
          <div className="w-2.5 h-2.5 rounded-full bg-slate-800 border border-slate-600 flex items-center justify-center animate-spin">
            <div className="w-1 h-1 rounded-full bg-slate-400" />
          </div>
        </div>

        {/* Battery box / Under-slung transformer equipment */}
        <div className="w-6 h-1.5 bg-slate-800 rounded-xs border border-slate-600" />

        {/* Bogie 2 */}
        <div className="flex items-center gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-slate-800 border border-slate-600 flex items-center justify-center animate-spin">
            <div className="w-1 h-1 rounded-full bg-slate-400" />
          </div>
          <div className="w-2 h-0.5 bg-slate-700" />
          <div className="w-2.5 h-2.5 rounded-full bg-slate-800 border border-slate-600 flex items-center justify-center animate-spin">
            <div className="w-1 h-1 rounded-full bg-slate-400" />
          </div>
        </div>
      </div>

      {/* Inter-coach coupler */}
      <div className="absolute right-[-4px] bottom-2 w-2 h-1 bg-slate-700" />
    </div>
  );
};
