import React from 'react';

export const CoreTelemetry: React.FC = () => {
  return (
    <article className="w-full rounded-3xl bg-white/[0.03] backdrop-blur-2xl border border-glass-border p-4 sm:p-6 shadow-xl flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <span className="font-mono text-[10px] uppercase text-text-muted tracking-wider">
          Suburban Core Telemetry
        </span>
        <span className="font-mono text-[11px] text-primary">CR-MAIN ONLINE</span>
      </div>

      <div className="grid grid-cols-2 gap-2 pt-1">
        <div className="p-3 rounded-2xl bg-white/[0.02] border border-glass-border">
          <span className="font-mono text-[10px] text-text-muted">Active Corridors</span>
          <div className="flex items-baseline gap-1 mt-1">
            <span className="font-headline text-2xl text-text-primary leading-none">128</span>
            <span className="font-mono text-[10px] text-primary">Rakes</span>
          </div>
        </div>
        <div className="p-3 rounded-2xl bg-white/[0.02] border border-glass-border">
          <span className="font-mono text-[10px] text-text-muted">OHE Traction</span>
          <div className="flex items-baseline gap-1 mt-1">
            <span className="font-headline text-2xl text-text-primary leading-none">25</span>
            <span className="font-mono text-[10px] text-primary">kV AC Nom</span>
          </div>
        </div>
      </div>

      {/* Interchange Flow Capacities */}
      <div className="flex flex-col gap-2.5 pt-2">
        <span className="font-mono text-[10px] uppercase text-text-muted tracking-wider">
          Terminal Inflow Stress
        </span>
        <div className="flex flex-col gap-1">
          <div className="flex items-center justify-between font-mono text-[11px]">
            <span className="text-text-secondary">Dadar Central (DR)</span>
            <span className="text-primary font-medium">94% Capacity</span>
          </div>
          <div className="w-full bg-white/[0.05] h-1.5 rounded-full overflow-hidden">
            <div className="bg-primary h-full rounded-full" style={{ width: '94%' }}></div>
          </div>
        </div>

        <div className="flex flex-col gap-1">
          <div className="flex items-center justify-between font-mono text-[11px]">
            <span className="text-text-secondary">Kurla Junction (CLA)</span>
            <span className="text-secondary font-medium">82% Capacity</span>
          </div>
          <div className="w-full bg-white/[0.05] h-1.5 rounded-full overflow-hidden">
            <div className="bg-secondary h-full rounded-full" style={{ width: '82%' }}></div>
          </div>
        </div>

        <div className="flex flex-col gap-1">
          <div className="flex items-center justify-between font-mono text-[11px]">
            <span className="text-text-secondary">Thane Node (TNA)</span>
            <span className="text-primary font-medium">88% Capacity</span>
          </div>
          <div className="w-full bg-white/[0.05] h-1.5 rounded-full overflow-hidden">
            <div className="bg-primary h-full rounded-full" style={{ width: '88%' }}></div>
          </div>
        </div>
      </div>
    </article>
  );
};
