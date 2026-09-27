import React from 'react';
import { motion } from 'framer-motion';

interface CorridorSelectorProps {
  origin: { code: string; name: string; platform: string; activeGate: string };
  destination: { code: string; name: string; campus: string };
  isReversed: boolean;
  fastOnly: boolean;
  onSwap: () => void;
  onToggleFastOnly: () => void;
  onSearch: () => void;
  isLoadingRakes?: boolean;
}

export const CorridorSelector: React.FC<CorridorSelectorProps> = ({
  origin,
  destination,
  isReversed,
  fastOnly,
  onSwap,
  onToggleFastOnly,
  onSearch,
  isLoadingRakes = false,
}) => {
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
              Origin Platform {origin.platform} • {isReversed ? 'UP Fast Track' : 'DOWN Through'}
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

        {/* Direction Swapper Capsule with 180° Framer Motion Spring Rotation */}
        <motion.button
          aria-label="Swap corridor route direction"
          onClick={onSwap}
          whileTap={{ scale: 0.9 }}
          className="w-10 h-10 rounded-full bg-white/[0.04] hover:bg-white/[0.1] active:bg-primary/20 transition-colors flex items-center justify-center shrink-0 border border-glass-border group cursor-pointer shadow-md"
        >
          <motion.span
            animate={{ rotate: isReversed ? 180 : 0 }}
            transition={{ type: 'spring', damping: 15, stiffness: 200 }}
            className="material-symbols-outlined text-text-secondary group-hover:text-primary text-[20px]"
          >
            sync_alt
          </motion.span>
        </motion.button>

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
          <button
            onClick={onToggleFastOnly}
            className={`hidden xl:flex items-center gap-1.5 px-3 py-1.5 rounded-full border transition-all cursor-pointer font-mono text-[10px] ${
              fastOnly
                ? 'bg-primary/20 border-primary/40 text-primary font-bold'
                : 'bg-white/[0.03] border-glass-border text-text-secondary hover:text-white'
            }`}
          >
            <span className={`w-1.5 h-1.5 rounded-full ${fastOnly ? 'bg-primary animate-ping' : 'bg-text-muted'}`}></span>
            <span>{fastOnly ? 'FAST RAKES ONLY' : 'ALL LOCAL & FAST'}</span>
          </button>

          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={onSearch}
            disabled={isLoadingRakes}
            className={`w-full sm:w-auto px-6 py-2.5 rounded-full font-body text-xs font-semibold transition-all flex items-center justify-center gap-2 cursor-pointer shadow-lg ${
              fastOnly
                ? 'bg-primary text-black hover:bg-primary-container shadow-primary/20'
                : 'bg-text-primary text-black hover:bg-white shadow-[0_0_24px_rgba(255,255,255,0.25)]'
            }`}
          >
            {isLoadingRakes ? (
              <>
                <span className="w-3.5 h-3.5 border-2 border-black border-t-transparent rounded-full animate-spin"></span>
                <span>Scanning Blocks...</span>
              </>
            ) : (
              <>
                <span>{fastOnly ? 'Show All Schedules' : 'Find Fast Rakes'}</span>
                <span className="material-symbols-outlined text-[18px]">bolt</span>
              </>
            )}
          </motion.button>
        </div>
      </div>
    </section>
  );
};
