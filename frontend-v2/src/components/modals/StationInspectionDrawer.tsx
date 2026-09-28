import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { StationTelemetry } from '../../lib/services/telemetryService';

interface StationInspectionDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  station: StationTelemetry | null;
}

export const StationInspectionDrawer: React.FC<StationInspectionDrawerProps> = ({
  isOpen,
  onClose,
  station,
}) => {
  if (!isOpen || !station) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          className="relative w-full max-w-lg p-6 rounded-3xl bg-surface-obsidian border border-glass-border shadow-2xl text-text-primary overflow-hidden"
        >
          {/* Header */}
          <div className="flex items-center justify-between pb-4 border-b border-glass-border">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center text-primary shrink-0">
                <span className="material-symbols-outlined text-[24px]">apartment</span>
              </div>
              <div className="flex flex-col">
                <div className="flex items-center gap-2">
                  <h3 className="font-headline text-2xl text-text-primary">{station.name}</h3>
                  <span className="px-2 py-0.5 rounded-full bg-primary/10 text-primary font-mono text-xs font-bold">
                    [{station.code}]
                  </span>
                </div>
                <span className="font-mono text-[10px] text-text-muted">
                  Chainage: {station.distanceKm.toFixed(1)} km from Origin
                </span>
              </div>
            </div>
            <button
              onClick={onClose}
              className="w-8 h-8 rounded-full bg-white/[0.04] hover:bg-white/[0.1] flex items-center justify-center text-text-muted hover:text-white transition-colors cursor-pointer"
            >
              <span className="material-symbols-outlined text-[18px]">close</span>
            </button>
          </div>

          {/* Timetable Schedule Strip */}
          <div className="grid grid-cols-3 gap-2 my-3 p-3 rounded-2xl bg-white/[0.03] border border-glass-border font-mono">
            <div className="flex flex-col">
              <span className="text-[10px] text-text-muted uppercase">Arr Time</span>
              <span className="text-sm font-bold text-primary">{station.arrivalTime || '--:--'}</span>
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] text-text-muted uppercase">Dep Time</span>
              <span className="text-sm font-bold text-text-primary">{station.departureTime || '--:--'}</span>
            </div>
            <div className="flex flex-col text-right">
              <span className="text-[10px] text-text-muted uppercase">Platform / Dwell</span>
              <span className="text-xs font-semibold text-secondary">
                {station.platform || 'PF 02'} • {station.dwellSeconds ? `${station.dwellSeconds}s` : 'Stop'}
              </span>
            </div>
          </div>

          {/* Platform Occupancy Matrix */}
          <div className="flex flex-col gap-3 my-2">
            <span className="font-mono text-[10px] uppercase text-text-muted tracking-wider">
              Live Platform Clearance & FOB Congestion
            </span>

            <div className="grid grid-cols-1 gap-2.5 max-h-64 overflow-y-auto pr-1">
              {station.platforms.map((plat) => (
                <div
                  key={plat.number}
                  className="p-3 rounded-2xl bg-white/[0.02] border border-glass-border flex flex-col gap-2"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs text-text-primary font-bold">
                        Platform {plat.number}
                      </span>
                      <span className="font-mono text-[10px] text-text-muted">
                        • Crossover Speed: {plat.crossoverSpeedKm} km/h
                      </span>
                    </div>
                    <span
                      className={`font-mono text-[10px] px-2 py-0.5 rounded-full font-semibold ${
                        plat.fobCongestion === 'CRITICAL'
                          ? 'bg-signal-rose/20 text-signal-rose'
                          : plat.fobCongestion === 'HIGH'
                          ? 'bg-secondary/20 text-secondary'
                          : 'bg-primary/20 text-primary'
                      }`}
                    >
                      FOB: {plat.fobCongestion}
                    </span>
                  </div>

                  {/* Occupancy bar */}
                  <div className="flex items-center gap-3">
                    <div className="flex-1 bg-white/[0.06] h-2 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          plat.occupancyPercent > 85
                            ? 'bg-signal-rose'
                            : plat.occupancyPercent > 70
                            ? 'bg-secondary'
                            : 'bg-primary'
                        }`}
                        style={{ width: `${plat.occupancyPercent}%` }}
                      ></div>
                    </div>
                    <span className="font-mono text-xs text-text-secondary font-medium w-9 text-right">
                      {plat.occupancyPercent}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Footer Info */}
          <div className="pt-3 border-t border-glass-border flex items-center justify-between font-mono text-[10px] text-text-muted">
            <span className="flex items-center gap-1.5 text-primary">
              <span className="w-1.5 h-1.5 rounded-full bg-primary animate-ping"></span>
              Optical Turnstile Sensors Active
            </span>
            <button
              onClick={onClose}
              className="px-4 py-1.5 rounded-full bg-white/[0.06] hover:bg-white/[0.12] text-text-primary transition-colors cursor-pointer"
            >
              Done
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
