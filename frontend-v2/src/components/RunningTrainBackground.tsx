import React, { useState } from "react";
import { useAuthStore, MUMBAI_COLLEGES } from "../store/useAuthStore";
import { Eye, Maximize2, Minimize2 } from "lucide-react";

interface RunningTrainProps {
  speed?: "normal" | "fast" | "slow";
}

export const RunningTrainBackground: React.FC<RunningTrainProps> = () => {
  const { selectedLine, selectedCollegeId } = useAuthStore();
  const [videoOpacity, setVideoOpacity] = useState<number>(0.65);
  const [showFrame, setShowFrame] = useState<boolean>(true);

  const selectedCollege =
    MUMBAI_COLLEGES.find((c) => c.id === selectedCollegeId) || MUMBAI_COLLEGES[0];

  return (
    <div
      className="fixed inset-0 pointer-events-none overflow-hidden z-0 select-none bg-slate-900"
      aria-hidden="true"
    >
      {/* 1. REAL MUMBAI LOCAL TRAIN VIDEO BACKGROUND (Pristine - No Watermarks, No Extra Vector Trains) */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <video
          autoPlay
          loop
          muted
          playsInline
          key="mumbai-local-real-video"
          className="w-full h-full object-cover object-center filter saturate-[1.15] contrast-[1.08] transition-opacity duration-700"
          style={{ opacity: videoOpacity }}
        >
          <source src="/videos/mumbai_local_bg.mp4" type="video/mp4" />
        </video>

        {/* Light-Grey Executive Frosted Glass Tint Overlay (Ensures 100% Card Readability) */}
        <div className="absolute inset-0 bg-gradient-to-b from-slate-100/75 via-slate-50/65 to-slate-200/80 backdrop-blur-[1px]" />
      </div>

      {/* 2. MUMBAI LOCAL COACH CABIN FRAME PERSPECTIVE */}
      {showFrame && (
        <div className="absolute inset-2 sm:inset-4 rounded-3xl border-2 sm:border-4 border-slate-300/60 shadow-[inset_0_0_40px_rgba(15,23,42,0.12)] pointer-events-none z-1 flex flex-col justify-between p-3 sm:p-5">
          {/* Top Frame Header with Interactive Controls */}
          <div className="flex justify-between items-center opacity-80">
            <div className="flex items-center gap-2 font-mono text-[9px] sm:text-[10px] text-slate-700 font-bold bg-white/85 backdrop-blur-md px-3 py-1.5 rounded-xl border border-slate-300/80 shadow-xs pointer-events-auto">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="hidden sm:inline">REAL MUMBAI LOCAL SUBURBAN VIDEO</span>
              <span className="sm:hidden">REAL EMU VIDEO</span>

              {/* Video Opacity Mode Switcher */}
              <div className="flex items-center gap-1 ml-2 pl-2 border-l border-slate-200">
                <button
                  type="button"
                  onClick={() => setVideoOpacity((prev) => (prev > 0.7 ? 0.45 : 0.85))}
                  className="px-2 py-0.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-800 text-[10px] font-mono font-bold transition-all border border-slate-300 cursor-pointer shadow-2xs active:scale-95 flex items-center gap-1"
                  title="Toggle Video Vibrancy"
                >
                  <Eye className="w-3 h-3 text-indigo-600" />
                  <span>{videoOpacity > 0.7 ? "Vivid (85%)" : "Soft (45%)"}</span>
                </button>

                <button
                  type="button"
                  onClick={() => setShowFrame(false)}
                  className="p-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 hover:text-slate-900 transition-colors"
                  title="Hide Cabin Window Frame"
                >
                  <Maximize2 className="w-3 h-3" />
                </button>
              </div>
            </div>

            <div className="font-hand text-xs sm:text-sm text-slate-700 font-bold bg-white/80 backdrop-blur-md px-3 py-1 rounded-xl border border-slate-300/80 shadow-xs">
              {selectedCollege.name.split("(")[0].trim()} • {selectedLine} Local 🚆
            </div>
          </div>

          {/* Bottom Frame Telemetry Stamp */}
          <div className="flex justify-between items-center opacity-70">
            <div className="font-mono text-[9px] text-slate-600 font-semibold bg-white/80 backdrop-blur-md px-2.5 py-1 rounded-lg border border-slate-300/70 shadow-2xs">
              MUMBAI CENTRAL DIVISION // LIVE RUNNING FOOTAGE
            </div>
            <div className="font-mono text-[9px] text-slate-600 font-semibold bg-white/80 backdrop-blur-md px-2.5 py-1 rounded-lg border border-slate-300/70 shadow-2xs">
              LOWER PAREL • ONE WORLD CENTER CORRIDOR
            </div>
          </div>
        </div>
      )}

      {/* Frame Restore Button when hidden */}
      {!showFrame && (
        <button
          type="button"
          onClick={() => setShowFrame(true)}
          className="absolute top-4 right-4 z-20 pointer-events-auto bg-white/80 hover:bg-white text-slate-700 px-3 py-1.5 rounded-xl border border-slate-300 shadow-sm font-mono text-xs flex items-center gap-1.5 transition-all"
        >
          <Minimize2 className="w-3.5 h-3.5" />
          <span>Show Frame</span>
        </button>
      )}

      {/* 3. Static Moiré Interference Pattern (Subtle dual gratings) */}
      <div
        className="absolute inset-0 opacity-[0.03] pointer-events-none"
        style={{
          backgroundImage: `
            repeating-linear-gradient(45deg, #64748b 0, #64748b 1px, transparent 0, transparent 16px),
            repeating-linear-gradient(48.5deg, #475569 0, #475569 1px, transparent 0, transparent 16px)
          `,
        }}
      />

      {/* 4. Fine Blueprint Grid Mesh */}
      <svg className="absolute inset-0 w-full h-full opacity-25 pointer-events-none" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="bg-grid-mesh" width="80" height="80" patternUnits="userSpaceOnUse">
            <path d="M 80 0 L 0 0 0 80" fill="none" stroke="rgba(148, 163, 184, 0.16)" strokeWidth="0.75" />
            <path d="M 40 0 L 40 80 M 0 40 L 80 40" fill="none" stroke="rgba(148, 163, 184, 0.08)" strokeWidth="0.5" strokeDasharray="2 3" />
            <circle cx="80" cy="0" r="1.5" fill="rgba(100, 116, 139, 0.15)" />
            <circle cx="0" cy="80" r="1.5" fill="rgba(100, 116, 139, 0.15)" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#bg-grid-mesh)" />
      </svg>
    </div>
  );
};
