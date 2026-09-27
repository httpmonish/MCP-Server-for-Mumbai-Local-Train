import React, { useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { RunningTrainBackground, type VideoClipId } from "./components/RunningTrainBackground";
import { Film, Sliders, Sparkles } from "lucide-react";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { refetchOnWindowFocus: false },
  },
});

export const MainCanvas: React.FC = () => {
  const [activeClip, setActiveClip] = useState<VideoClipId>("station_1080");
  const [dimLevel, setDimLevel] = useState(25);
  const [showControls, setShowControls] = useState(false);

  return (
    <div className="relative min-h-screen w-full flex flex-col justify-between p-6 sm:p-10 z-10 select-none">
      {/* ── True 1080p Full HD Video Backdrop ── */}
      <RunningTrainBackground clipId={activeClip} dimLevel={dimLevel} />

      {/* ── Top Floating Bar with HD Video Switcher & Status ── */}
      <div className="relative z-10 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl overflow-hidden border border-white/20 shadow-2xl shadow-black/50">
            <img src="/logo.jpg" alt="TransitPulse Logo" className="w-full h-full object-cover" />
          </div>
          <div>
            <h1 className="text-base font-extrabold text-white font-heading tracking-tight drop-shadow-lg">
              TransitPulse
            </h1>
            <p className="text-[11px] font-mono text-cyan-300 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              1080p Full HD Video Active
            </p>
          </div>
        </div>

        {/* HD Video Controller Pill */}
        <div className="relative">
          <button
            onClick={() => setShowControls(!showControls)}
            className="px-3.5 py-2 rounded-xl bg-black/50 backdrop-blur-xl border border-white/15 text-white hover:bg-black/70 transition-all flex items-center gap-2 text-xs font-mono shadow-xl"
          >
            <Film className="w-3.5 h-3.5 text-cyan-400" />
            <span>HD Video Options</span>
            <Sliders className="w-3 h-3 text-slate-400" />
          </button>

          {showControls && (
            <div className="absolute right-0 mt-2 w-72 p-4 rounded-2xl bg-slate-950/90 backdrop-blur-2xl border border-cyan-500/30 shadow-2xl z-50 text-xs space-y-3">
              <div>
                <span className="font-bold font-heading text-white block mb-2">
                  Select 1080p Video Clip:
                </span>
                <div className="space-y-1.5">
                  <button
                    onClick={() => setActiveClip("station_1080")}
                    className={`w-full py-2 px-3 rounded-xl font-mono text-left text-[11px] font-semibold border transition-all flex items-center justify-between ${
                      activeClip === "station_1080"
                        ? "bg-cyan-600 text-white border-cyan-400 shadow-md"
                        : "bg-slate-900/80 text-slate-300 border-white/5 hover:border-white/20"
                    }`}
                  >
                    <span>1. Station Express (1080p HD)</span>
                    {activeClip === "station_1080" && <Sparkles className="w-3.5 h-3.5 text-white" />}
                  </button>

                  <button
                    onClick={() => setActiveClip("city_1080")}
                    className={`w-full py-2 px-3 rounded-xl font-mono text-left text-[11px] font-semibold border transition-all flex items-center justify-between ${
                      activeClip === "city_1080"
                        ? "bg-cyan-600 text-white border-cyan-400 shadow-md"
                        : "bg-slate-900/80 text-slate-300 border-white/5 hover:border-white/20"
                    }`}
                  >
                    <span>2. City Corridor (1080p HD)</span>
                    {activeClip === "city_1080" && <Sparkles className="w-3.5 h-3.5 text-white" />}
                  </button>

                  <button
                    onClick={() => setActiveClip("mumbai_classic")}
                    className={`w-full py-2 px-3 rounded-xl font-mono text-left text-[11px] font-semibold border transition-all flex items-center justify-between ${
                      activeClip === "mumbai_classic"
                        ? "bg-cyan-600 text-white border-cyan-400 shadow-md"
                        : "bg-slate-900/80 text-slate-300 border-white/5 hover:border-white/20"
                    }`}
                  >
                    <span>3. Mumbai Local Classic</span>
                    {activeClip === "mumbai_classic" && <Sparkles className="w-3.5 h-3.5 text-white" />}
                  </button>
                </div>
              </div>

              <div className="pt-2 border-t border-white/10">
                <div className="flex items-center justify-between font-mono text-[11px] text-slate-300 mb-1">
                  <span>Overlay Tint / Dim</span>
                  <span className="text-cyan-400 font-bold">{dimLevel}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="80"
                  value={dimLevel}
                  onChange={(e) => setDimLevel(Number(e.target.value))}
                  className="w-full accent-cyan-400 cursor-pointer"
                />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ── Center Zero State Notice ── */}
      <div className="relative z-10 text-center max-w-lg mx-auto py-12">
        <div className="p-6 rounded-3xl bg-black/45 backdrop-blur-2xl border border-white/15 shadow-2xl shadow-black/80">
          <div className="inline-flex p-2.5 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 mb-3">
            <Sparkles className="w-6 h-6" />
          </div>
          <h2 className="text-xl font-extrabold text-white font-heading tracking-tight mb-2">
            1080p Full HD Video Engine Ready
          </h2>
          <p className="text-xs text-white/80 font-body leading-relaxed">
            The background has been upgraded with razor-sharp 1080p high definition video. Tell me how you'd like to structure the new interface from scratch!
          </p>
        </div>
      </div>

      {/* ── Bottom status ── */}
      <div className="relative z-10 flex items-center justify-between text-[11px] font-mono text-white/70 bg-black/30 backdrop-blur-md px-4 py-2 rounded-full border border-white/10">
        <span>Active Resolution: 1920 × 1080 (60 FPS Full HD)</span>
        <span>Ready for new layout build</span>
      </div>
    </div>
  );
};

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <MainCanvas />
    </QueryClientProvider>
  );
}
