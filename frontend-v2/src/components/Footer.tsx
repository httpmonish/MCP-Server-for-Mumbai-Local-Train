import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="relative z-10 w-full bg-surface-obsidian/90 backdrop-blur-xl border-t border-glass-border py-6 mt-10">
      <div className="max-w-[1440px] mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-3 font-mono text-[11px] text-text-muted">
        <div className="flex items-center gap-3">
          <span>
            LATENCY: <span className="text-primary font-semibold">42ms</span>
          </span>
          <span className="text-glass-border">•</span>
          <span>GPS DISPATCH: KALYAN-CHURCHGATE FEED ACTIVE</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="font-headline-italic italic text-sm text-text-secondary leading-none">
            मुंबईTeleport
          </span>
          <span className="text-text-muted">© 2026 Central &amp; Western Railway Suburban Mesh.</span>
        </div>
      </div>
    </footer>
  );
};
