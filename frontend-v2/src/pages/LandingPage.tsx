import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion, useScroll, useTransform, AnimatePresence } from 'framer-motion';

/* ─── LIVE STATS TICKER DATA ─── */
const TICKER_ITEMS = [
  { label: 'Daily Ridership', value: '7.5M+', icon: 'groups' },
  { label: 'Active Rakes', value: '198', icon: 'train' },
  { label: 'Lines Tracked', value: '4', icon: 'route' },
  { label: 'Avg Headway', value: '3m 40s', icon: 'timer' },
  { label: 'Signal Blocks', value: '312', icon: 'cell_tower' },
  { label: 'Stations', value: '120+', icon: 'location_on' },
];

const LINE_CORRIDORS = [
  { name: 'Central Line', color: '#DC2626', stations: 'CSMT → Kasara/Khopoli', desc: 'Main spine of Mumbai suburban — through Dadar, Kurla, Thane to Kalyan & beyond.' },
  { name: 'Western Line', color: '#3B82F6', stations: 'Churchgate → Dahanu Road', desc: 'Western corridor running along the coast — Bandra, Andheri, Borivali to Virar.' },
  { name: 'Harbour Line', color: '#10B981', stations: 'CSMT → Panvel', desc: 'Trans-island connectivity — Wadala, Vashi, Nerul connecting Navi Mumbai.' },
  { name: 'Trans-Harbour', color: '#F59E0B', stations: 'Thane → Panvel', desc: 'Cross-harbour link connecting Thane to Navi Mumbai via Vashi & Airoli.' },
];

const FEATURES = [
  { title: 'Live Block Clearance Map', desc: 'Track every signal block across all corridors in real-time. Watch trains move through sections with TMS-grade accuracy.', icon: 'map', accent: '#DC2626' },
  { title: 'Smart Route Planner', desc: 'Find the fastest rake between any two stations. Filter by Fast, Slow, AC — with actual departure and arrival times.', icon: 'alt_route', accent: '#3B82F6' },
  { title: 'Delay Certificate Engine', desc: 'Generate SHA-256 signed Central Railway delay certificates with GPS proof — accepted by colleges and employers.', icon: 'verified_user', accent: '#10B981' },
  { title: 'Multi-Persona Intelligence', desc: 'Switch between Commuter, Student, and Corporate modes for contextual commute telemetry and risk analysis.', icon: 'person_search', accent: '#F59E0B' },
];

/* ─── SCROLL REVEAL COMPONENT ─── */
const Reveal: React.FC<{ children: React.ReactNode; delay?: number; direction?: 'up' | 'left' | 'right' }> = ({
  children,
  delay = 0,
  direction = 'up',
}) => {
  const ref = useRef<HTMLDivElement>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) setIsVisible(true); },
      { threshold: 0.15, rootMargin: '0px 0px -40px 0px' }
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  const initial = direction === 'up'
    ? { opacity: 0, y: 40 }
    : direction === 'left'
    ? { opacity: 0, x: -40 }
    : { opacity: 0, x: 40 };

  return (
    <motion.div
      ref={ref}
      initial={initial}
      animate={isVisible ? { opacity: 1, y: 0, x: 0 } : initial}
      transition={{ duration: 0.7, delay, ease: [0.16, 1, 0.3, 1] }}
    >
      {children}
    </motion.div>
  );
};

/* ─── ANIMATED TRAIN SVG ─── */
const AnimatedTrain: React.FC = () => {
  return (
    <div className="relative w-full h-16 overflow-hidden my-8">
      {/* Track Line */}
      <div className="absolute top-1/2 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-white/10 to-transparent" />
      {/* Station Dots */}
      {[10, 25, 40, 55, 70, 85].map((pos, i) => (
        <div
          key={i}
          className="absolute top-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-white/20 border border-white/10"
          style={{ left: `${pos}%` }}
        />
      ))}
      {/* Moving Train */}
      <motion.div
        className="absolute top-1/2 -translate-y-1/2"
        animate={{ left: ['2%', '92%'] }}
        transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
      >
        <div className="relative flex items-center">
          <div className="w-3 h-3 rounded-full bg-[#DC2626] shadow-[0_0_16px_rgba(220,38,38,0.8)]" />
          <div className="absolute -top-6 left-1/2 -translate-x-1/2 whitespace-nowrap">
            <span className="font-mono text-[9px] text-[#DC2626] font-bold tracking-wider">● LIVE</span>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

/* ─── LANDING PAGE ─── */
export const LandingPage: React.FC = () => {
  const heroRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll();
  const orbScale = useTransform(scrollYProgress, [0, 0.3], [1, 1.5]);
  const orbOpacity = useTransform(scrollYProgress, [0, 0.4], [0.6, 0]);
  const [hoveredLine, setHoveredLine] = useState<number | null>(null);

  return (
    <div className="min-h-screen bg-[#080c14] text-white font-body selection:bg-red-500/30 selection:text-white overflow-x-hidden">
      {/* ═══ NAVIGATION ═══ */}
      <nav className="fixed top-0 w-full z-50 bg-[#080c14]/80 backdrop-blur-2xl border-b border-white/[0.06]">
        <div className="max-w-[1400px] mx-auto px-6 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-baseline gap-1.5 group">
            <span className="font-headline text-xl tracking-tight text-white/90">
              मुंबई<span className="font-body text-sm font-semibold text-[#DC2626] tracking-normal">Teleport</span>
            </span>
          </Link>
          <div className="hidden md:flex items-center gap-8">
            <a href="#corridors" className="font-mono text-[11px] text-white/50 hover:text-white/90 transition-colors tracking-wider uppercase">Corridors</a>
            <a href="#features" className="font-mono text-[11px] text-white/50 hover:text-white/90 transition-colors tracking-wider uppercase">Features</a>
            <a href="#telemetry" className="font-mono text-[11px] text-white/50 hover:text-white/90 transition-colors tracking-wider uppercase">Telemetry</a>
          </div>
          <div className="flex items-center gap-3">
            <Link
              to="/login"
              className="font-mono text-[11px] text-white/60 hover:text-white transition-colors tracking-wider uppercase"
            >
              Sign In
            </Link>
            <Link
              to="/trains"
              className="px-5 py-2 rounded-full bg-[#DC2626] hover:bg-[#EF4444] text-white font-body text-xs font-semibold transition-all shadow-[0_0_20px_rgba(220,38,38,0.3)] hover:shadow-[0_0_32px_rgba(220,38,38,0.5)]"
            >
              Open Dashboard →
            </Link>
          </div>
        </div>
      </nav>

      {/* ═══ HERO SECTION ═══ */}
      <section ref={heroRef} className="relative min-h-screen flex flex-col items-center justify-center px-6 pt-16 overflow-hidden">
        {/* Animated Red Orb */}
        <motion.div
          style={{ scale: orbScale, opacity: orbOpacity }}
          className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] rounded-full pointer-events-none"
        >
          <div className="w-full h-full rounded-full bg-[radial-gradient(circle,rgba(220,38,38,0.35)_0%,rgba(220,38,38,0.08)_45%,transparent_70%)] animate-pulse" />
          <div className="absolute inset-8 rounded-full bg-[radial-gradient(circle,rgba(220,38,38,0.2)_0%,transparent_60%)] blur-xl" />
        </motion.div>

        {/* Grid Background */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:60px_60px] pointer-events-none" />

        {/* Hero Content */}
        <div className="relative z-10 max-w-4xl mx-auto text-center flex flex-col items-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="flex items-center gap-2 mb-6"
          >
            <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/[0.04] border border-white/[0.08] font-mono text-[10px] text-white/50 tracking-widest uppercase">
              <span className="w-1.5 h-1.5 rounded-full bg-[#DC2626] animate-pulse" />
              Mumbai Suburban Flow Telemetry
            </span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.1 }}
            className="font-headline text-5xl sm:text-6xl md:text-7xl tracking-tight leading-[1.05] mb-6"
          >
            <span className="text-white/90">Track Every</span>
            <br />
            <span className="text-[#DC2626]">Mumbai Local</span>
            <br />
            <span className="text-white/60 text-4xl sm:text-5xl md:text-6xl">in Real Time</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.25 }}
            className="max-w-xl text-white/40 font-body text-sm sm:text-base leading-relaxed mb-10"
          >
            Block-by-block signal telemetry across Central, Western, Harbour & Trans-Harbour corridors.
            Plan your commute with live rake tracking and smart journey intelligence.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.35 }}
            className="flex flex-col sm:flex-row items-center gap-4"
          >
            <Link
              to="/trains"
              className="group px-8 py-3.5 rounded-full bg-[#DC2626] hover:bg-[#EF4444] text-white font-body text-sm font-semibold transition-all shadow-[0_4px_24px_rgba(220,38,38,0.35)] hover:shadow-[0_8px_40px_rgba(220,38,38,0.5)] flex items-center gap-2"
            >
              <span>Open Live Dashboard</span>
              <span className="material-symbols-outlined text-[18px] group-hover:translate-x-0.5 transition-transform">arrow_forward</span>
            </Link>
            <a
              href="#corridors"
              className="px-8 py-3.5 rounded-full bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] hover:border-white/[0.15] text-white/70 hover:text-white font-body text-sm transition-all"
            >
              Explore Corridors
            </a>
          </motion.div>
        </div>

        {/* Animated Train Track */}
        <div className="relative z-10 w-full max-w-3xl mx-auto mt-16">
          <AnimatedTrain />
        </div>

        {/* Scroll Indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5 }}
          className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2"
        >
          <span className="font-mono text-[9px] text-white/25 tracking-widest uppercase">Scroll</span>
          <motion.div
            animate={{ y: [0, 6, 0] }}
            transition={{ duration: 1.5, repeat: Infinity }}
            className="w-4 h-7 rounded-full border border-white/15 flex items-start justify-center pt-1.5"
          >
            <div className="w-1 h-1.5 rounded-full bg-white/30" />
          </motion.div>
        </motion.div>
      </section>

      {/* ═══ LIVE STATS TICKER ═══ */}
      <section className="py-6 border-y border-white/[0.04] bg-white/[0.01] overflow-hidden">
        <div className="animate-ticker">
          {[...TICKER_ITEMS, ...TICKER_ITEMS].map((item, i) => (
            <div key={i} className="flex items-center gap-6 px-8 shrink-0">
              <div className="flex items-center gap-2.5">
                <span className="material-symbols-outlined text-[16px] text-[#DC2626]/70">{item.icon}</span>
                <span className="font-mono text-[11px] text-white/30 tracking-wider uppercase whitespace-nowrap">{item.label}</span>
                <span className="font-mono text-sm text-white/80 font-bold tabular-nums">{item.value}</span>
              </div>
              <span className="text-white/10">│</span>
            </div>
          ))}
        </div>
      </section>

      {/* ═══ CORRIDOR LINES SECTION ═══ */}
      <section id="corridors" className="py-24 px-6">
        <div className="max-w-[1200px] mx-auto">
          <Reveal>
            <div className="text-center mb-16">
              <span className="font-mono text-[10px] text-[#DC2626] tracking-[0.2em] uppercase">Network Coverage</span>
              <h2 className="font-headline text-4xl sm:text-5xl text-white/90 mt-3 tracking-tight">Four Corridors. One Pulse.</h2>
              <p className="font-body text-sm text-white/35 mt-4 max-w-lg mx-auto">
                Complete coverage of Mumbai's suburban railway network — from CSMT to Dahanu Road, Panvel to Kasara.
              </p>
            </div>
          </Reveal>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {LINE_CORRIDORS.map((line, i) => (
              <Reveal key={i} delay={i * 0.1}>
                <motion.div
                  onHoverStart={() => setHoveredLine(i)}
                  onHoverEnd={() => setHoveredLine(null)}
                  className="relative p-6 rounded-2xl bg-white/[0.02] border border-white/[0.06] hover:border-white/[0.12] transition-all cursor-pointer overflow-hidden group"
                >
                  {/* Color accent glow */}
                  <AnimatePresence>
                    {hoveredLine === i && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="absolute inset-0 pointer-events-none"
                        style={{
                          background: `radial-gradient(circle at 80% 80%, ${line.color}15 0%, transparent 60%)`,
                        }}
                      />
                    )}
                  </AnimatePresence>

                  <div className="relative z-10 flex items-start gap-4">
                    <div
                      className="w-3 h-3 rounded-full mt-1 shrink-0 shadow-lg"
                      style={{ backgroundColor: line.color, boxShadow: `0 0 12px ${line.color}60` }}
                    />
                    <div className="flex flex-col gap-2">
                      <div className="flex items-baseline gap-3">
                        <h3 className="font-body text-lg text-white/90 font-semibold">{line.name}</h3>
                        <span className="font-mono text-[10px] text-white/30 tracking-wider">{line.stations}</span>
                      </div>
                      <p className="font-body text-xs text-white/40 leading-relaxed">{line.desc}</p>
                    </div>
                  </div>
                </motion.div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ FEATURES SECTION ═══ */}
      <section id="features" className="py-24 px-6 bg-white/[0.01]">
        <div className="max-w-[1200px] mx-auto">
          <Reveal>
            <div className="text-center mb-16">
              <span className="font-mono text-[10px] text-[#DC2626] tracking-[0.2em] uppercase">Capabilities</span>
              <h2 className="font-headline text-4xl sm:text-5xl text-white/90 mt-3 tracking-tight">Built for Mumbai's Lifeline</h2>
              <p className="font-body text-sm text-white/35 mt-4 max-w-lg mx-auto">
                Every feature is engineered for the 7.5 million daily riders who depend on this network.
              </p>
            </div>
          </Reveal>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            {FEATURES.map((feat, i) => (
              <Reveal key={i} delay={i * 0.08} direction={i % 2 === 0 ? 'left' : 'right'}>
                <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/[0.06] hover:border-white/[0.12] transition-all group">
                  <div className="flex items-start gap-4">
                    <div
                      className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 transition-colors"
                      style={{ backgroundColor: `${feat.accent}15` }}
                    >
                      <span
                        className="material-symbols-outlined text-[20px]"
                        style={{ color: feat.accent }}
                      >
                        {feat.icon}
                      </span>
                    </div>
                    <div className="flex flex-col gap-1.5">
                      <h3 className="font-body text-sm text-white/90 font-semibold">{feat.title}</h3>
                      <p className="font-body text-xs text-white/35 leading-relaxed">{feat.desc}</p>
                    </div>
                  </div>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ TELEMETRY PREVIEW SECTION ═══ */}
      <section id="telemetry" className="py-24 px-6">
        <div className="max-w-[1200px] mx-auto">
          <Reveal>
            <div className="text-center mb-16">
              <span className="font-mono text-[10px] text-[#DC2626] tracking-[0.2em] uppercase">Static Telemetry Preview</span>
              <h2 className="font-headline text-4xl sm:text-5xl text-white/90 mt-3 tracking-tight">Signal-Grade Precision</h2>
              <p className="font-body text-sm text-white/35 mt-4 max-w-lg mx-auto">
                Infrastructure telemetry modeled after Indian Railway TMS block clearance systems.
              </p>
            </div>
          </Reveal>

          <Reveal delay={0.15}>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {[
                { label: 'Signal Blocks', value: '312', sub: 'Active Monitoring' },
                { label: 'Avg Speed', value: '62 km/h', sub: 'Peak Hours' },
                { label: 'Track Circuits', value: '1,440', sub: 'Axle Counter Based' },
                { label: 'Platform Feeds', value: '120+', sub: 'GPS Integrated' },
              ].map((stat, i) => (
                <div key={i} className="p-5 rounded-2xl bg-white/[0.02] border border-white/[0.06] text-center flex flex-col gap-1">
                  <span className="font-mono text-2xl text-white/90 font-bold tabular-nums">{stat.value}</span>
                  <span className="font-mono text-[10px] text-white/40 tracking-wider uppercase">{stat.label}</span>
                  <span className="font-mono text-[9px] text-[#DC2626]/60">{stat.sub}</span>
                </div>
              ))}
            </div>
          </Reveal>

          <Reveal delay={0.25}>
            <div className="mt-6 p-4 rounded-2xl bg-white/[0.02] border border-white/[0.06] flex items-center gap-3">
              <span className="material-symbols-outlined text-[16px] text-amber-500/70">warning</span>
              <span className="font-mono text-[11px] text-amber-500/70 tracking-wider">
                STATIC DATA — Telemetry values are deterministic simulations. No live railway API integration.
              </span>
            </div>
          </Reveal>
        </div>
      </section>

      {/* ═══ CTA SECTION ═══ */}
      <section className="py-32 px-6 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(220,38,38,0.08)_0%,transparent_50%)] pointer-events-none" />
        <div className="relative z-10 max-w-2xl mx-auto text-center flex flex-col items-center gap-8">
          <Reveal>
            <h2 className="font-headline text-4xl sm:text-5xl text-white/90 tracking-tight">
              Your Commute.<br />
              <span className="text-[#DC2626]">Teleported.</span>
            </h2>
          </Reveal>
          <Reveal delay={0.1}>
            <p className="font-body text-sm text-white/35 max-w-md">
              Access real-time suburban train telemetry, route planning, and commute intelligence — completely free and open source.
            </p>
          </Reveal>
          <Reveal delay={0.2}>
            <Link
              to="/trains"
              className="px-10 py-4 rounded-full bg-[#DC2626] hover:bg-[#EF4444] text-white font-body text-sm font-semibold transition-all shadow-[0_4px_32px_rgba(220,38,38,0.4)] hover:shadow-[0_8px_48px_rgba(220,38,38,0.6)] flex items-center gap-2"
            >
              <span>Launch Dashboard</span>
              <span className="material-symbols-outlined text-[18px]">rocket_launch</span>
            </Link>
          </Reveal>
        </div>
      </section>

      {/* ═══ FOOTER ═══ */}
      <footer className="py-8 px-6 border-t border-white/[0.04]">
        <div className="max-w-[1200px] mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="font-headline text-base text-white/40">
              मुंबई<span className="font-body text-xs font-semibold text-[#DC2626]/60">Teleport</span>
            </span>
            <span className="font-mono text-[10px] text-white/20">© 2026 Suburban Flow Telemetry</span>
          </div>
          <div className="flex items-center gap-6">
            <span className="font-mono text-[10px] text-white/20 tracking-wider">
              LATENCY: <span className="text-[#DC2626]/60">42ms</span>
            </span>
            <span className="text-white/10">│</span>
            <span className="font-mono text-[10px] text-white/20 tracking-wider">STATIC DATA MODE</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
