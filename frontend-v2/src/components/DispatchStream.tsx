import React from 'react';

export const DispatchStream: React.FC = () => {
  const logs = [
    {
      time: '08:44',
      title: 'TNA Platform 5 Clear',
      desc: 'Rake #95401 received automatic route line to Up Fast through Track 1.',
      color: 'text-text-primary',
      badge: 'text-text-muted',
    },
    {
      time: '08:41',
      title: 'Kurla Slow Crossover Regulated',
      desc: 'Speed restriction 30 km/h active due to freight crossover handoff.',
      color: 'text-secondary',
      badge: 'text-secondary',
    },
    {
      time: '08:38',
      title: 'AC Special #95403 Departure Ready',
      desc: 'Kalyan shed sync confirmed. Medha traction inverter diagnostics green.',
      color: 'text-primary',
      badge: 'text-primary',
    },
  ];

  return (
    <article className="w-full rounded-3xl bg-white/[0.03] backdrop-blur-2xl border border-glass-border p-4 sm:p-6 shadow-xl flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <span className="font-mono text-[10px] uppercase text-text-muted tracking-wider flex items-center gap-1.5 font-semibold">
          <span className="w-1.5 h-1.5 rounded-full bg-primary"></span>
          Dispatch Log (TMS Live Feed)
        </span>
        <span className="font-mono text-[9px] text-text-muted">CSMT DISPATCH</span>
      </div>

      <div className="flex flex-col gap-3 pt-2">
        {logs.map((log, index) => (
          <div
            key={index}
            className={`flex items-start gap-3 ${
              index !== logs.length - 1 ? 'pb-3 border-b border-white/[0.04]' : ''
            }`}
          >
            <span className={`font-mono text-[10px] ${log.badge} pt-0.5 shrink-0`}>
              {log.time}
            </span>
            <div className="flex flex-col gap-0.5">
              <span className={`font-body text-xs ${log.color} font-medium`}>{log.title}</span>
              <span className="font-body text-[11px] text-text-secondary leading-snug">
                {log.desc}
              </span>
            </div>
          </div>
        ))}
      </div>
    </article>
  );
};
