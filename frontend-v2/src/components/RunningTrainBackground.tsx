import React, { useMemo } from "react";
import { useAuthStore } from "../store/useAuthStore";

interface RunningTrainProps {
  speed?: "normal" | "fast" | "slow";
}

export const RunningTrainBackground: React.FC<RunningTrainProps> = () => {
  const { selectedLine } = useAuthStore();

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
      {/* 1. Base Light Grey Architectural Canvas */}
      <div className="absolute inset-0 bg-gradient-to-b from-slate-100 via-slate-50/70 to-slate-200/90" />

      {/* 2. Static Moiré Interference Pattern (Subtle 45° vs 48.5° dual gratings) */}
      <div
        className="absolute inset-0 opacity-[0.05]"
        style={{
          backgroundImage: `
            repeating-linear-gradient(45deg, #64748b 0, #64748b 1px, transparent 0, transparent 14px),
            repeating-linear-gradient(48.5deg, #475569 0, #475569 1px, transparent 0, transparent 14px)
          `,
        }}
      />

      {/* 3. Dynamic Ambient Moiré Drift Layer */}
      <div
        className="absolute inset-0 opacity-[0.035] animate-moire-drift"
        style={{
          backgroundImage: `
            repeating-linear-gradient(135deg, #0284c7 0, #0284c7 1.5px, transparent 0, transparent 24px),
            repeating-linear-gradient(137.5deg, #6366f1 0, #6366f1 1.5px, transparent 0, transparent 24px)
          `,
          backgroundSize: "200% 200%",
        }}
      />

      {/* 4. Fine Blueprint Grid Mesh */}
      <svg className="absolute inset-0 w-full h-full opacity-40" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="bg-grid-mesh" width="80" height="80" patternUnits="userSpaceOnUse">
            <path d="M 80 0 L 0 0 0 80" fill="none" stroke="rgba(148, 163, 184, 0.18)" strokeWidth="0.75" />
            <path d="M 40 0 L 40 80 M 0 40 L 80 40" fill="none" stroke="rgba(148, 163, 184, 0.08)" strokeWidth="0.5" strokeDasharray="2 3" />
            <circle cx="80" cy="0" r="1.5" fill="rgba(100, 116, 139, 0.2)" />
            <circle cx="0" cy="80" r="1.5" fill="rgba(100, 116, 139, 0.2)" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#bg-grid-mesh)" />
      </svg>

      {/* 5. Distant Sahyadri Mountains / Mumbai High-Rise Skyline Silhouettes */}
      <div className="absolute bottom-28 left-0 right-0 h-36 opacity-20 pointer-events-none">
        <svg viewBox="0 0 1400 120" preserveAspectRatio="none" className="w-full h-full text-slate-500 fill-current">
          {/* Subtle rolling Sahyadri Thal Ghats & Mumbai suburban outline */}
          <path d="M 0 120 L 0 85 Q 90 50, 180 70 T 360 55 T 540 85 T 720 50 T 900 70 T 1080 45 T 1260 75 T 1400 65 L 1400 120 Z" />
          {/* Transmission towers */}
          <rect x="260" y="45" width="2" height="30" />
          <path d="M 254 55 L 266 55 M 256 65 L 264 65" stroke="currentColor" strokeWidth="1.5" />
          <rect x="850" y="35" width="2" height="40" />
          <path d="M 844 45 L 856 45 M 846 58 L 854 58" stroke="currentColor" strokeWidth="1.5" />
        </svg>
      </div>

      {/* 6. RAILWAY CORRIDOR INFRASTRUCTURE (Catenary, Masts, Rails, Sleepers) */}
      <div className="absolute bottom-0 left-0 right-0 h-36 pointer-events-none">
        {/* Overhead 25 kV AC Catenary Wire */}
        <div className="absolute top-3 left-0 right-0 h-[1.5px] bg-slate-400/70" />
        {/* Contact Wire (where pantograph touches) */}
        <div className="absolute top-10 left-0 right-0 h-[1.5px] bg-amber-700/60 shadow-xs" />

        {/* Dropper Wires */}
        <div className="absolute top-3 left-0 right-0 h-7 flex justify-between px-3 opacity-35">
          {Array.from({ length: 40 }).map((_, i) => (
            <div key={i} className="w-[1px] h-full bg-slate-500" />
          ))}
        </div>

        {/* OHE Steel Lattice Portal Masts */}
        <div className="absolute top-0 left-0 right-0 h-32 flex justify-between px-12 opacity-40">
          {Array.from({ length: 7 }).map((_, i) => (
            <div key={i} className="flex flex-col items-center">
              <div className="w-10 h-2.5 border-t-2 border-slate-600 -mt-1" />
              <div className="w-3 h-28 border-l border-r border-slate-600 relative">
                {/* Cross Bracing */}
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

        {/* 3-Aspect Automatic Block Signaling */}
        <div className="absolute top-6 right-36 flex flex-col items-center opacity-70">
          <div className="w-3.5 h-9 rounded-md bg-slate-900 p-0.5 flex flex-col justify-between items-center shadow-md border border-slate-700">
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_10px_#34D399]" />
            <div className="w-2 h-2 rounded-full bg-slate-800" />
            <div className="w-2 h-2 rounded-full bg-slate-800" />
          </div>
          <div className="w-1.5 h-20 bg-slate-700" />
        </div>

        {/* Concrete Viaduct Deck & Ballast Bed */}
        <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-b from-slate-300 via-slate-400/80 to-slate-500 border-t-2 border-slate-400 shadow-inner" />

        {/* Pre-stressed Concrete Sleepers */}
        <div className="absolute bottom-7 left-0 right-0 h-7 flex justify-between px-1 opacity-60">
          {Array.from({ length: 90 }).map((_, i) => (
            <div key={i} className="w-2 h-full bg-slate-700 rounded-xs shadow-xs" />
          ))}
        </div>

        {/* Double Running Rails (Steel 60kg/m) with gleaming rail-head shine */}
        <div className="absolute bottom-13 left-0 right-0 h-1.5 bg-gradient-to-b from-slate-200 via-slate-500 to-slate-800 shadow-[0_1px_3px_rgba(0,0,0,0.4)]" />
        <div className="absolute bottom-9 left-0 right-0 h-1.5 bg-gradient-to-b from-slate-200 via-slate-500 to-slate-800 shadow-[0_1px_3px_rgba(0,0,0,0.4)]" />
      </div>

      {/* 7. AUTHENTIC DYNAMIC RUNNING MUMBAI LOCAL EMU TRAIN */}
      {/* Moves smoothly across the screen in an infinite traversing loop */}
      <div className="absolute bottom-11 left-0 w-full overflow-visible pointer-events-none animate-train-traverse">
        <div className="inline-flex items-end relative filter drop-shadow-lg">
          {/* Volumetric Headlight High-Beam sweeping forward onto track */}
          <div className="absolute -right-48 bottom-3 w-64 h-16 bg-gradient-to-r from-amber-300/40 via-amber-200/20 to-transparent transform -skew-x-12 blur-xs pointer-events-none" />

          {/* Coach 1: Trailing Cab Coach */}
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

          {/* Coach 5: Leading Driver Cab (Distinctive Aerodynamic Front Nose) */}
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
// Features: Siemens/Bombardier curved nose, grab rails, commuter silhouettes,
// stainless steel fluted rib panels, yellow/maroon/navy racing stripes,
// destination LED display, spinning wheel bogies, pantograph sparks.
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
      {/* 1. ROOF EQUIPMENT & PANTOGRAPH */}
      <div className="w-full h-7 relative flex justify-center items-end">
        {hasPantograph && (
          <div className="w-20 h-7 relative flex flex-col items-center justify-end -mb-0.5">
            {/* Carbon Contact Strip sliding on 25kV Catenary */}
            <div className="w-14 h-1 bg-slate-900 relative rounded-full">
              {/* Electric Contact Arc Spark (Cyan Glow) */}
              <div className="absolute -top-1.5 left-5 w-3 h-3 rounded-full bg-cyan-300 animate-spark opacity-90 blur-xs" />
              <div className="absolute -top-1 left-9 w-2 h-2 rounded-full bg-white animate-pulse" />
            </div>
            {/* Pantograph Scissor Articulated Frame */}
            <div className="w-8 h-5 border-t-2 border-l border-r border-slate-800 -rotate-12 transform origin-bottom scale-y-110" />
            {/* High Voltage Base Insulators (Orange Ceramic) */}
            <div className="w-12 h-1.5 flex justify-between px-1">
              <div className="w-1.5 h-1.5 rounded-full bg-amber-600 border border-slate-800" />
              <div className="w-1.5 h-1.5 rounded-full bg-amber-600 border border-slate-800" />
              <div className="w-1.5 h-1.5 rounded-full bg-amber-600 border border-slate-800" />
            </div>
          </div>
        )}

        {/* Roof Air Vents & Resistor Banks */}
        {!hasPantograph && (
          <div className="w-3/4 h-2 flex justify-around px-2 mb-0.5">
            <div className="w-8 h-1.5 bg-slate-400 rounded-t-sm border-t border-slate-500" />
            <div className="w-8 h-1.5 bg-slate-400 rounded-t-sm border-t border-slate-500" />
            <div className="w-8 h-1.5 bg-slate-400 rounded-t-sm border-t border-slate-500" />
          </div>
        )}
      </div>

      {/* 2. MAIN EMU COACH BODY */}
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
        {/* Stainless Steel Fluted Corrugated Roof Ribs */}
        <div className="w-full h-1.5 bg-slate-300/90 border-b border-slate-400/60 flex justify-between px-1">
          <div className="w-full h-0.5 bg-slate-400/40 mt-0.5" />
        </div>

        {/* Upper Yellow Safety Stripe */}
        <div className="w-full h-1" style={{ backgroundColor: livery.secondaryStripe }} />

        {/* WINDOWS & OPEN DOORWAYS ROW */}
        <div className="flex items-center justify-between px-2 py-0.5">
          {/* Rear Driver Windshield (if trailing cab) */}
          {isCab && !isLeading && (
            <div className="w-4 h-6 bg-slate-800 rounded-l-md border border-slate-600 shadow-inner flex items-center justify-center">
              <div className="w-1 h-3 bg-red-600 rounded-xs shadow-[0_0_5px_#DC2626]" />
            </div>
          )}

          {/* MUMBAI LOCAL DOORWAY 1 (Wide Open with Center Grab Pole) */}
          <div className="w-5 h-8 bg-slate-900 rounded-xs border border-slate-700 relative overflow-hidden flex items-center justify-center">
            {/* Stainless steel center divider pole */}
            <div className="w-0.5 h-full bg-slate-300 z-10" />
            {/* Commuter silhouette standing at doorway */}
            <div className="absolute bottom-0 left-0.5 w-2 h-5 bg-slate-700/80 rounded-t-xs" />
          </div>

          {/* PASSENGER WINDOW BAY (Warm Interior Lighting + Guard Grills) */}
          <div className="flex gap-1.5">
            <div className="w-6 h-5 bg-amber-100/90 border border-slate-500 rounded-xs shadow-inner relative overflow-hidden flex flex-col justify-center">
              {/* Window horizontal protection bars */}
              <div className="w-full h-[0.5px] bg-slate-600/60 my-0.5" />
              <div className="w-full h-[0.5px] bg-slate-600/60" />
              {/* Commuter silhouette */}
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

          {/* MUMBAI LOCAL DOORWAY 2 */}
          <div className="w-5 h-8 bg-slate-900 rounded-xs border border-slate-700 relative overflow-hidden flex items-center justify-center">
            <div className="w-0.5 h-full bg-slate-300 z-10" />
            <div className="absolute bottom-0 right-0.5 w-2 h-5 bg-slate-700/80 rounded-t-xs" />
          </div>

          {/* LEADING DRIVER CAB FRONT NOSE (Curved Aerodynamic Windshield + LED Board) */}
          {isCab && isLeading && (
            <div className="flex flex-col items-end gap-0.5 mr-0.5">
              {/* Amber LED Destination Display Board */}
              {destinationText && (
                <div className="bg-black text-amber-400 font-mono text-[6px] px-1.5 py-0.2 rounded-xs tracking-tighter uppercase font-black shadow-xs border border-amber-500/40">
                  {destinationText}
                </div>
              )}

              {/* Curved Windshield with Driver Silhouette */}
              <div className="w-8 h-6 bg-gradient-to-r from-slate-900 to-sky-950 rounded-r-2xl border-2 border-slate-600 shadow-inner flex items-center justify-between px-1 relative">
                {/* Windshield wiper */}
                <div className="w-2.5 h-0.5 bg-slate-400 rotate-45 transform origin-left" />

                {/* TWIN HIGH-INTENSITY LED HEADLIGHTS */}
                <div className="flex flex-col gap-0.5">
                  <div className="w-2 h-2 rounded-full bg-amber-200 shadow-[0_0_8px_#FEF08A] border border-amber-300 animate-pulse" />
                  <div className="w-2 h-2 rounded-full bg-amber-200 shadow-[0_0_8px_#FEF08A] border border-amber-300 animate-pulse" />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Accent Pinstripe */}
        <div className="w-full h-0.5" style={{ backgroundColor: livery.accentPinstripe }} />

        {/* ICONIC LOWER RACING STRIPE (Central Maroon / Western Navy / Harbour Emerald) */}
        <div
          className="w-full h-3 flex items-center justify-between px-2.5 relative"
          style={{ backgroundColor: livery.primaryStripe }}
        >
          {/* Coach Number Designation */}
          <span className="font-mono text-[7px] text-white font-black uppercase tracking-widest">
            {coachNumber}
          </span>
          {/* Middle yellow hazard warning band on nose */}
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

      {/* 3. UNDERCARRIAGE BOGIES & STEEL WHEELS */}
      <div className="w-full flex justify-around px-4 -mt-1">
        {/* Bogie 1 (Front Axle) */}
        <div className="flex items-center gap-2 bg-slate-900/90 px-1 py-0.5 rounded-sm border border-slate-700">
          <div className="w-3.5 h-3.5 rounded-full bg-slate-800 border-2 border-slate-500 flex items-center justify-center animate-spin">
            <div className="w-1 h-1 rounded-full bg-slate-400" />
          </div>
          <div className="w-2 h-1 bg-amber-700 rounded-xs" />
          <div className="w-3.5 h-3.5 rounded-full bg-slate-800 border-2 border-slate-500 flex items-center justify-center animate-spin">
            <div className="w-1 h-1 rounded-full bg-slate-400" />
          </div>
        </div>

        {/* Bogie 2 (Rear Axle) */}
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
