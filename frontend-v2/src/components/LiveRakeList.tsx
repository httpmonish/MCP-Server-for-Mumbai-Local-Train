import React, { useState } from 'react';

export const LiveRakeList: React.FC = () => {
  const [expandedRake, setExpandedRake] = useState<string | null>('95401');

  const toggleDrawer = (id: string) => {
    setExpandedRake(expandedRake === id ? null : id);
  };

  return (
    <section className="flex flex-col gap-4">
      {/* Section Header */}
      <div className="flex items-end justify-between px-1 pb-2">
        <div className="flex flex-col">
          <span className="font-mono text-[11px] uppercase text-text-muted tracking-widest">
            Down Local / Fast Telemetry
          </span>
          <div className="flex items-baseline gap-2 mt-0.5">
            <h2 className="font-headline text-3xl tracking-tight text-text-primary">Today’s Flow</h2>
            <span className="font-headline-italic italic text-xl text-text-secondary">
              VJTI Morning Corridors
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-3 py-1 rounded-full bg-white/[0.04] border border-glass-border font-mono text-[11px] text-text-secondary">
            3 Rakes in 28m Window
          </span>
        </div>
      </div>

      {/* Train Card 1: Train #95401 FAST (12-Car Rake) [FEATURED] */}
      <article className="w-full rounded-3xl bg-white/[0.03] backdrop-blur-2xl border border-glass-border p-4 sm:p-6 transition-all duration-300 hover:bg-white/[0.05] hover:border-glass-border-hover shadow-xl flex flex-col gap-4 group">
        {/* Top Telemetry Row */}
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-1 rounded-full bg-primary/10 text-primary font-mono text-[11px] uppercase flex items-center gap-1.5 font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-primary animate-ping"></span>
              On Schedule
            </span>
            <span className="px-2.5 py-1 rounded-full bg-white/[0.04] text-text-secondary font-mono text-[11px]">
              #95401 FAST
            </span>
            <span className="hidden sm:inline font-mono text-[11px] text-text-muted">
              • 12-Car ICF Siemens Rake
            </span>
          </div>
          <div className="flex items-center gap-3 font-mono text-[11px] text-text-secondary">
            <span className="flex items-center gap-1 text-primary">
              <span className="material-symbols-outlined text-[16px]">speed</span>
              92 km/h
            </span>
            <span className="text-text-muted">•</span>
            <span className="px-2 py-0.5 rounded-full bg-white/[0.04]">Plat 5 (TNA)</span>
          </div>
        </div>

        {/* Times & Destinations */}
        <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-3 py-1">
          <div className="flex items-baseline gap-3">
            <span className="font-headline text-3xl text-text-primary tracking-tight font-normal">
              08:47 AM
            </span>
            <span className="font-body text-sm text-text-muted font-light">Thane Dep</span>
            <span className="material-symbols-outlined text-text-muted text-[18px] translate-y-0.5">
              trending_flat
            </span>
            <span className="font-headline text-3xl text-primary tracking-tight font-normal">
              09:23 AM
            </span>
            <span className="font-body text-sm text-text-muted font-light">Dadar Arr</span>
          </div>
          <div className="flex flex-col sm:items-end">
            <span className="font-mono text-lg text-text-primary font-medium tracking-tight">
              36 mins
            </span>
            <span className="font-body text-xs text-text-muted">
              7 Stops (Non-stop GC → CLA)
            </span>
          </div>
        </div>

        {/* Occupancy & VJTI Target Delta */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-1">
          <div className="p-3 rounded-2xl bg-white/[0.02] border border-glass-border flex items-center justify-between">
            <span className="font-body text-xs text-text-muted">Total Load</span>
            <span className="font-mono text-xs text-primary font-medium">78% (Moderate Density)</span>
          </div>
          <div className="p-3 rounded-2xl bg-white/[0.02] border border-glass-border flex items-center justify-between">
            <span className="font-body text-xs text-text-muted">VJTI Walk</span>
            <span className="font-mono text-xs text-text-primary font-medium">6 mins from Matunga E.</span>
          </div>
          <div className="p-3 rounded-2xl bg-white/[0.02] border border-glass-border flex items-center justify-between">
            <span className="font-body text-xs text-text-muted">Arrival Buffer</span>
            <span className="font-mono text-xs text-primary font-medium">+12m Before Lecture</span>
          </div>
        </div>

        {/* Interactive Carriage Density Forecaster Accordion */}
        <div className="w-full pt-1">
          <button
            onClick={() => toggleDrawer('95401')}
            className="w-full py-2 px-3 rounded-2xl bg-white/[0.02] hover:bg-white/[0.04] border border-glass-border transition-colors flex items-center justify-between font-body text-xs text-text-secondary group-hover:text-text-primary cursor-pointer"
          >
            <span className="flex items-center gap-2">
              <span className="material-symbols-outlined text-[18px] text-primary">view_column</span>
              <span>Carriage-by-Carriage Real-time Crowding Matrix (12 Cars)</span>
            </span>
            <div className="flex items-center gap-1 font-mono text-xs text-text-muted">
              <span>{expandedRake === '95401' ? 'Collapse' : 'View Carriage Map'}</span>
              <span
                className={`material-symbols-outlined text-[16px] transition-transform duration-300 ${
                  expandedRake === '95401' ? 'rotate-180' : ''
                }`}
              >
                expand_more
              </span>
            </div>
          </button>

          {/* Expandable Drawer Compartment */}
          {expandedRake === '95401' && (
            <div className="flex flex-col gap-3 pt-4 px-2">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {/* Coach 1-3 */}
                <div className="p-3 rounded-xl bg-surface-container-high/60 border border-glass-border flex flex-col gap-2">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-[11px] text-text-primary">C1-C3 Gen II</span>
                    <span className="font-mono text-[10px] text-secondary">86%</span>
                  </div>
                  <div className="w-full bg-white/[0.06] h-1.5 rounded-full overflow-hidden">
                    <div className="bg-secondary h-full rounded-full" style={{ width: '86%' }}></div>
                  </div>
                  <span className="font-mono text-[10px] text-text-muted">Boarding doors 2 & 3 busy</span>
                </div>

                {/* Coach 4 */}
                <div className="p-3 rounded-xl bg-surface-container-high/60 border border-glass-border flex flex-col gap-2">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-[11px] text-text-primary">C4 First Class</span>
                    <span className="font-mono text-[10px] text-primary">54%</span>
                  </div>
                  <div className="w-full bg-white/[0.06] h-1.5 rounded-full overflow-hidden">
                    <div className="bg-primary h-full rounded-full" style={{ width: '54%' }}></div>
                  </div>
                  <span className="font-mono text-[10px] text-text-muted">Comfort seats available</span>
                </div>

                {/* Coach 5 */}
                <div className="p-3 rounded-xl bg-surface-container-high/60 border border-glass-border flex flex-col gap-2">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-[11px] text-text-primary">C5 Ladies Compartment</span>
                    <span className="font-mono text-[10px] text-primary">62%</span>
                  </div>
                  <div className="w-full bg-white/[0.06] h-1.5 rounded-full overflow-hidden">
                    <div className="bg-primary h-full rounded-full" style={{ width: '62%' }}></div>
                  </div>
                  <span className="font-mono text-[10px] text-text-muted">Smooth transit flow</span>
                </div>

                {/* Coach 6-12 */}
                <div className="p-3 rounded-xl bg-surface-container-high/60 border border-glass-border flex flex-col gap-2">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-[11px] text-text-primary">C6 Divyang / Vendor</span>
                    <span className="font-mono text-[10px] text-primary">40%</span>
                  </div>
                  <div className="w-full bg-white/[0.06] h-1.5 rounded-full overflow-hidden">
                    <div className="bg-primary h-full rounded-full" style={{ width: '40%' }}></div>
                  </div>
                  <span className="font-mono text-[10px] text-text-muted">Unimpeded ingress</span>
                </div>
              </div>

              <div className="flex items-center justify-between font-mono text-[11px] text-text-muted pt-1">
                <span>Teleport Predictive Flow Sensor V3.2 • Calibrated 08:35 AM</span>
                <span className="text-primary cursor-pointer hover:underline">
                  Select Best Coach Location →
                </span>
              </div>
            </div>
          )}
        </div>
      </article>

      {/* Train Card 2: Train #95201 SLOW (12-Car Rake) [DELAYED] */}
      <article className="w-full rounded-3xl bg-white/[0.03] backdrop-blur-2xl border border-glass-border p-4 sm:p-6 transition-all duration-300 hover:bg-white/[0.05] shadow-xl flex flex-col gap-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-1 rounded-full bg-secondary/20 text-secondary font-mono text-[11px] uppercase flex items-center gap-1.5 font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-secondary animate-pulse"></span>
              Delayed +6m
            </span>
            <span className="px-2.5 py-1 rounded-full bg-white/[0.04] text-text-secondary font-mono text-[11px]">
              #95201 SLOW
            </span>
            <span className="hidden sm:inline font-mono text-[11px] text-text-muted">
              • 12-Car Local All-Stops
            </span>
          </div>
          <div className="flex items-center gap-2 font-mono text-[11px] text-secondary">
            <span className="material-symbols-outlined text-[16px]">info</span>
            <span>Signaling hold-up at Kurla Platform 1</span>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-3 py-1">
          <div className="flex items-baseline gap-3">
            <div className="flex items-baseline gap-1.5">
              <span className="font-headline text-3xl text-text-primary tracking-tight font-normal">
                09:08 AM
              </span>
              <span className="font-mono text-xs text-secondary line-through">09:02</span>
            </div>
            <span className="font-body text-sm text-text-muted font-light">Thane Dep</span>
            <span className="material-symbols-outlined text-text-muted text-[18px] translate-y-0.5">
              trending_flat
            </span>
            <span className="font-headline text-3xl text-text-secondary tracking-tight font-normal">
              10:07 AM
            </span>
            <span className="font-body text-sm text-text-muted font-light">Dadar Arr</span>
          </div>
          <div className="flex flex-col sm:items-end">
            <span className="font-mono text-lg text-secondary font-medium tracking-tight">
              59 mins
            </span>
            <span className="font-body text-xs text-text-muted">
              14 Stops (Heavy Mulund/Bhandup Dwell)
            </span>
          </div>
        </div>

        <div className="p-3 rounded-2xl bg-secondary/10 border border-secondary/20 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-secondary text-[18px]">warning</span>
            <span className="font-body text-xs text-secondary">
              Risk for 09:30 Academic Slot: ETA Dadar arrives after 10:00 AM. Avoid this corridor.
            </span>
          </div>
          <span className="font-mono text-[10px] text-secondary font-medium uppercase tracking-wider">
            Unrecommended
          </span>
        </div>
      </article>

      {/* Train Card 3: Train #95403 AC FAST [PREMIUM] */}
      <article className="w-full rounded-3xl bg-white/[0.03] backdrop-blur-2xl border border-glass-border p-4 sm:p-6 transition-all duration-300 hover:bg-white/[0.05] shadow-xl flex flex-col gap-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-1 rounded-full bg-primary/20 text-primary font-mono text-[11px] uppercase flex items-center gap-1.5 font-semibold">
              <span className="material-symbols-outlined text-[14px]">ac_unit</span>
              Air-Conditioned EMU
            </span>
            <span className="px-2.5 py-1 rounded-full bg-white/[0.04] text-text-secondary font-mono text-[11px]">
              #95403 AC FAST
            </span>
            <span className="hidden sm:inline font-mono text-[11px] text-text-muted">
              • Medha Automatic Doors
            </span>
          </div>
          <div className="flex items-center gap-3 font-mono text-[11px] text-primary">
            <span className="px-2 py-0.5 rounded-full bg-white/[0.04] text-text-primary">
              Cabin 21.0°C
            </span>
            <span className="text-text-muted">•</span>
            <span>UTS QR Valid</span>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-3 py-1">
          <div className="flex items-baseline gap-3">
            <span className="font-headline text-3xl text-text-primary tracking-tight font-normal">
              09:15 AM
            </span>
            <span className="font-body text-sm text-text-muted font-light">Thane Dep</span>
            <span className="material-symbols-outlined text-text-muted text-[18px] translate-y-0.5">
              trending_flat
            </span>
            <span className="font-headline text-3xl text-primary tracking-tight font-normal">
              09:51 AM
            </span>
            <span className="font-body text-sm text-text-muted font-light">Dadar Arr</span>
          </div>
          <div className="flex flex-col sm:items-end">
            <span className="font-mono text-lg text-text-primary font-medium tracking-tight">
              36 mins
            </span>
            <span className="font-body text-xs text-text-muted">High Comfort Corridor</span>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-between gap-2 pt-1 font-body text-xs text-text-secondary">
          <span>Automated plug-doors initiate close 20 seconds prior to whistle.</span>
          <button className="px-4 py-1.5 rounded-full bg-white/[0.06] hover:bg-white/[0.12] text-text-primary transition-all font-mono text-[11px] cursor-pointer">
            Verify Pass Validity →
          </button>
        </div>
      </article>
    </section>
  );
};
