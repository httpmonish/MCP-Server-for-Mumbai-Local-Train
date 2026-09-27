import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export const GapAnalysisDrawer: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.shiftKey && (e.key === 'G' || e.key === 'g')) {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <>
      {/* Floating Developer Badge Trigger */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-4 left-4 z-40 px-3 py-1.5 rounded-full bg-surface-obsidian/90 backdrop-blur-xl border border-glass-border shadow-2xl hover:border-primary/50 text-text-secondary hover:text-primary transition-all flex items-center gap-2 font-mono text-[11px] cursor-pointer group"
      >
        <span className="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
        <span>Gap Analysis (Ctrl+Shift+G)</span>
      </button>

      {/* Drawer Modal */}
      <AnimatePresence>
        {isOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              transition={{ type: 'spring', damping: 25, stiffness: 300 }}
              className="relative w-full max-w-3xl max-h-[85vh] p-6 rounded-3xl bg-surface-obsidian border border-glass-border shadow-2xl text-text-primary overflow-hidden flex flex-col"
            >
              {/* Header */}
              <div className="flex items-center justify-between pb-4 border-b border-glass-border shrink-0">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center text-primary shrink-0">
                    <span className="material-symbols-outlined text-[22px]">troubleshoot</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="font-mono text-[10px] uppercase text-primary font-bold tracking-widest">
                      Engineering Architecture • Bidirectional Analysis
                    </span>
                    <h3 className="font-headline text-2xl text-text-primary">
                      Suburban Flow & MCP Telemetry Gap Report
                    </h3>
                  </div>
                </div>
                <button
                  onClick={() => setIsOpen(false)}
                  className="w-8 h-8 rounded-full bg-white/[0.04] hover:bg-white/[0.1] flex items-center justify-center text-text-muted hover:text-white transition-colors cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[18px]">close</span>
                </button>
              </div>

              {/* Scrollable Content Matrix */}
              <div className="flex-1 overflow-y-auto my-4 pr-1 flex flex-col gap-6">
                {/* Category A */}
                <div className="flex flex-col gap-2">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-secondary"></span>
                    <h4 className="font-mono text-xs uppercase font-bold text-secondary tracking-wider">
                      Category A: Frontend Rendered, Backend Missing (Needs Integration)
                    </h4>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs font-mono">
                    <div className="p-3 rounded-xl bg-white/[0.02] border border-glass-border flex flex-col gap-1">
                      <span className="text-text-primary font-semibold">1. Coach-by-Coach Live Load Matrix</span>
                      <span className="text-text-muted text-[11px]">Requires bogie weight transducer or optical AI feed from platform edge.</span>
                    </div>
                    <div className="p-3 rounded-xl bg-white/[0.02] border border-glass-border flex flex-col gap-1">
                      <span className="text-text-primary font-semibold">2. Automated College Biometric Sync</span>
                      <span className="text-text-muted text-[11px]">Requires ERP webhook integration with VJTI / SPIT academic portals.</span>
                    </div>
                    <div className="p-3 rounded-xl bg-white/[0.02] border border-glass-border flex flex-col gap-1">
                      <span className="text-text-primary font-semibold">3. Cryptographic SHA-256 Delay Slip</span>
                      <span className="text-text-muted text-[11px]">Central Railway official TMS digital signature verification endpoint.</span>
                    </div>
                    <div className="p-3 rounded-xl bg-white/[0.02] border border-glass-border flex flex-col gap-1">
                      <span className="text-text-primary font-semibold">4. Live Cabin HVAC Sensors</span>
                      <span className="text-text-muted text-[11px]">Medha AC rake IoT temperature telemetry hook.</span>
                    </div>
                  </div>
                </div>

                {/* Category B */}
                <div className="flex flex-col gap-2">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-primary"></span>
                    <h4 className="font-mono text-xs uppercase font-bold text-primary tracking-wider">
                      Category B: Backend Capable, Frontend Missing (To Expose on UI)
                    </h4>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs font-mono">
                    <div className="p-3 rounded-xl bg-white/[0.02] border border-glass-border flex flex-col gap-1">
                      <span className="text-text-primary font-semibold">1. Sunday Mega Block & Jumbo Block</span>
                      <span className="text-text-muted text-[11px]">Pre-scheduled maintenance track occupations between Matunga & Mulund.</span>
                    </div>
                    <div className="p-3 rounded-xl bg-white/[0.02] border border-glass-border flex flex-col gap-1">
                      <span className="text-text-primary font-semibold">2. Fast/Slow Track Crossover Signals</span>
                      <span className="text-text-muted text-[11px]">Real-time switch points at Kurla and Vidyavihar crossovers.</span>
                    </div>
                    <div className="p-3 rounded-xl bg-white/[0.02] border border-glass-border flex flex-col gap-1">
                      <span className="text-text-primary font-semibold">3. 12-Car vs 15-Car Platform Markers</span>
                      <span className="text-text-muted text-[11px]">Platform end stop indicators for extended suburban rakes.</span>
                    </div>
                    <div className="p-3 rounded-xl bg-white/[0.02] border border-glass-border flex flex-col gap-1">
                      <span className="text-text-primary font-semibold">4. Harbour Line Wadala Loop Reroute</span>
                      <span className="text-text-muted text-[11px]">Automatic rerouting telemetry via Wadala Road interchange loop.</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Footer */}
              <div className="pt-3 border-t border-glass-border flex items-center justify-between font-mono text-[11px] text-text-muted shrink-0">
                <span>See BACKEND_GAP_ANALYSIS.md for full architectural RFC</span>
                <button
                  onClick={() => setIsOpen(false)}
                  className="px-4 py-1.5 rounded-full bg-primary-container text-black font-semibold hover:bg-primary transition-all cursor-pointer"
                >
                  Close Drawer
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
};
