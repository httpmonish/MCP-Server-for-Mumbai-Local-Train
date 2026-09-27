import React, { useState } from 'react';

interface CorridorSelectorProps {
  origin: { code: string; name: string; platform: string; activeGate: string };
  destination: { code: string; name: string; campus: string };
  onSwap: () => void;
  onSearch: () => void;
}

export const CorridorSelector: React.FC<CorridorSelectorProps> = ({
  origin,
  destination,
  onSwap,
  onSearch,
}) => {
  const [swapping, setSwapping] = useState(false);

  const handleSwap = () => {
    setSwapping(true);
    onSwap();
    setTimeout(() => setSwapping(false), 300);
  };

  return (
    <section className="w-full">
      <div className="p-2 sm:p-2.5 rounded-3xl sm:rounded-full bg-white/[0.03] backdrop-blur-2xl border border-glass-border shadow-2xl flex flex-col md:flex-row items-center justify-between gap-3">
        {/* Origin Capsule */}
        <div className="flex items-center gap-3 w-full md:w-auto px-4 py-1.5 rounded-full bg-white/[0.02] hover:bg-white/[0.05] transition-all cursor-pointer group">
          <div className="w-9 h-9 rounded-full bg-primary/20 flex items-center justify-center shrink-0">
            <span className="material-symbols-outlined text-primary text-[20px]">train</span>
          </div>
          <div className="flex flex-col">
            <span className="font-mono text-[10px] text-text-muted tracking-wider uppercase">
              Origin Platform {origin.platform}
            </span>
            <div className="flex items-baseline gap-2">
              <span className="font-body text-sm text-text-primary font-medium tracking-tight">
                {origin.name}
              </span>
              <span className="font-mono text-xs text-primary font-medium">[{origin.code}]</span>
              <span className="hidden xl:inline text-text-muted text-xs font-light">
                • {origin.activeGate}
              </span>
            </div>
          </div>
        </div>

        {/* Direction Swapper Capsule */}
        <button
          aria-label="Swap corridor route"
          onClick={handleSwap}
          className="w-9 h-9 rounded-full bg-white/[0.04] hover:bg-white/[0.1] active:scale-95 transition-all duration-300 flex items-center justify-center shrink-0 border border-glass-border group"
        >
          <span
            className={`material-symbols-outlined text-text-secondary group-hover:text-primary transition-transform duration-500 text-[18px] ${
              swapping ? 'rotate-180 scale-90' : ''
            }`}
          >
            sync_alt
          </span>
        </button>

        {/* Destination Capsule */}
        <div className="flex items-center gap-3 w-full md:w-auto px-4 py-1.5 rounded-full bg-white/[0.02] hover:bg-white/[0.05] transition-all cursor-pointer group">
          <div className="w-9 h-9 rounded-full bg-surface-container-high flex items-center justify-center shrink-0">
            <span className="material-symbols-outlined text-secondary text-[20px]">near_me</span>
          </div>
          <div className="flex flex-col">
            <span className="font-mono text-[10px] text-text-muted tracking-wider uppercase">
              Destination Transit Hub
            </span>
            <div className="flex items-baseline gap-2">
              <span className="font-body text-sm text-text-primary font-medium tracking-tight">
                {destination.name}
              </span>
              <span className="font-mono text-xs text-secondary font-medium">
                [{destination.code}]
              </span>
              <span className="text-text-muted text-xs hidden lg:inline">• {destination.campus}</span>
            </div>
          </div>
        </div>

        {/* Filter Pill Chips & CTA Button */}
        <div className="flex items-center gap-2 w-full md:w-auto justify-end px-1">
          <div className="hidden xl:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/[0.03] border border-glass-border">
            <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"></span>
            <span className="font-mono text-[10px] text-text-secondary">FAST CORRIDOR ACTIVE</span>
          </div>
          <button
            onClick={onSearch}
            className="w-full sm:w-auto px-6 py-2.5 rounded-full bg-text-primary text-black font-body text-xs font-semibold hover:bg-white hover:shadow-[0_0_24px_rgba(255,255,255,0.25)] active:scale-95 transition-all flex items-center justify-center gap-2 cursor-pointer"
          >
            <span>Find Fast Rakes</span>
            <span className="material-symbols-outlined text-[18px]">bolt</span>
          </button>
        </div>
      </div>
    </section>
  );
};
