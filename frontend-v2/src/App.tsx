import React, { useEffect, useState, useRef } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { AttendanceCard } from "./components/AttendanceCard";
import { TrainTrackerCard } from "./components/TrainTrackerCard";
import { RunningTrainBackground } from "./components/RunningTrainBackground";
import { useAuthStore, MUMBAI_COLLEGES, DEMO_PROFILES } from "./store/useAuthStore";
import { useNetworkStatus } from "./hooks/useTrains";
import {
  CheckCircle2,
  Clock,
  GraduationCap,
  KeyRound,
  Radio,
  Train,
  Zap,
  Building2,
  UserCheck,
  ArrowRight,
  ChevronRight,
} from "lucide-react";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { refetchOnWindowFocus: false },
  },
});

/* ─── Ticker content ─── */
const TICKER_ITEMS = [
  "CR KASARA CORRIDOR — 37 STATIONS ACTIVE",
  "WR VIRAR FAST — PUNCTUALITY 99.1%",
  "HR PANVEL SERVICE — ON TIME",
  "SUBURBAN RADAR LIVE — MCP ENGINE v2.5",
  "CSMT ↔ KASARA — FULL TOPOLOGY VERIFIED",
  "AUTOMATED ATTENDANCE SYNC — ENABLED",
  "MUMBAI SUBURBAN RAILWAY NETWORK — OPERATIONAL",
];

/* ─── Animated counter ─── */
function useCounter(target: number, duration = 1200) {
  const [value, setValue] = useState(0);
  useEffect(() => {
    let start = 0;
    const step = Math.ceil(target / (duration / 16));
    const timer = setInterval(() => {
      start += step;
      if (start >= target) { setValue(target); clearInterval(timer); }
      else setValue(start);
    }, 16);
    return () => clearInterval(timer);
  }, [target, duration]);
  return value;
}

export const Dashboard: React.FC = () => {
  const {
    studentId, username, selectedLine, selectedCollegeId, activeProfileId,
    setStudentId, setCredentials, setSelectedCollegeId, loadDemoProfile,
  } = useAuthStore();

  const [showConfig, setShowConfig] = useState(false);
  const [tempId, setTempId]         = useState(studentId);
  const [tempUser, setTempUser]     = useState(username);
  const [tempPass, setTempPass]     = useState("");
  const [currentTime, setCurrentTime] = useState(new Date());
  const [mounted, setMounted]       = useState(false);

  const { data: networkStatus } = useNetworkStatus();

  useEffect(() => { setMounted(true); }, []);
  useEffect(() => {
    const t = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setStudentId(tempId);
    setCredentials(tempUser, tempPass);
    setShowConfig(false);
  };

  const selectedCollege = MUMBAI_COLLEGES.find((c) => c.id === selectedCollegeId) || MUMBAI_COLLEGES[0];

  const hours   = currentTime.getHours().toString().padStart(2, "0");
  const minutes = currentTime.getMinutes().toString().padStart(2, "0");
  const seconds = currentTime.getSeconds().toString().padStart(2, "0");

  const tickerContent = TICKER_ITEMS.join("  ·  ") + "  ·  ";

  return (
    <div style={{ minHeight: "100vh", position: "relative", overflowX: "hidden", color: "var(--c-white)" }}>
      {/* ── Scan line ── */}
      <div className="tp-scanline" />

      {/* ── 1. Video Background ── */}
      <RunningTrainBackground />

      {/* ── 2. Ticker Bar ── */}
      <div className="tp-ticker-bar relative z-30 py-2">
        <div style={{ display: "flex", alignItems: "center", gap: 16, overflow: "hidden" }}>
          {/* Live badge */}
          <div style={{
            flexShrink: 0, display: "flex", alignItems: "center", gap: 8,
            padding: "4px 16px", borderRight: "1px solid rgba(171,255,2,0.15)",
          }}>
            <span className="tp-lime-dot-pulse" />
            <span className="tp-label" style={{ color: "var(--c-lime)" }}>LIVE</span>
          </div>
          {/* Scrolling ticker */}
          <div style={{ flex: 1, overflow: "hidden" }}>
            <div className="tp-ticker-track tp-label" style={{ color: "var(--c-gray-dim)" }}>
              {tickerContent}{tickerContent}
            </div>
          </div>
          {/* IST Clock */}
          <div style={{
            flexShrink: 0, display: "flex", alignItems: "center", gap: 8,
            padding: "4px 16px", borderLeft: "1px solid rgba(171,255,2,0.15)",
          }}>
            <span className="tp-label" style={{ color: "var(--c-gray-dim)" }}>IST</span>
            <span className="tp-label-lg" style={{ color: "var(--c-white)" }}>
              {hours}:{minutes}:{seconds}
            </span>
          </div>
        </div>
      </div>

      {/* ── 3. Main Header ── */}
      <header className="tp-header relative z-30 px-6 sm:px-10 py-4 sticky top-0">
        <div style={{ maxWidth: 1400, margin: "0 auto", display: "flex", justifyContent: "space-between", alignItems: "center", gap: 16 }}>
          {/* Logo + Wordmark */}
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <div style={{ position: "relative", flexShrink: 0 }}>
              <img
                src="/logo.jpg"
                alt="TransitPulse Logo"
                style={{
                  width: 44, height: 44, borderRadius: 10,
                  objectFit: "cover",
                  border: "1px solid rgba(171,255,2,0.3)",
                  boxShadow: "0 0 20px rgba(171,255,2,0.15)",
                  transition: "box-shadow 0.3s",
                }}
                onMouseEnter={e => (e.currentTarget.style.boxShadow = "0 0 32px rgba(171,255,2,0.35)")}
                onMouseLeave={e => (e.currentTarget.style.boxShadow = "0 0 20px rgba(171,255,2,0.15)")}
              />
              {/* Live indicator */}
              <span style={{
                position: "absolute", top: -3, right: -3,
                width: 10, height: 10, borderRadius: "50%",
                background: "var(--c-lime)",
                boxShadow: "0 0 8px var(--c-lime)",
                border: "2px solid var(--c-void)",
              }} />
            </div>

            <div>
              <div style={{ display: "flex", alignItems: "baseline", gap: 10 }}>
                <h1 className="tp-h1" style={{ fontSize: "1.375rem", color: "var(--c-white)" }}>
                  Transit<span style={{ color: "var(--c-lime)" }}>Pulse</span>
                </h1>
                <span className="tp-label" style={{
                  color: "var(--c-lime)", background: "rgba(171,255,2,0.08)",
                  border: "1px solid rgba(171,255,2,0.25)", padding: "2px 10px", borderRadius: 2,
                }}>
                  MCP ENGINE
                </span>
              </div>
              <p className="tp-label" style={{ color: "var(--c-gray-dim)", marginTop: 4 }}>
                Mumbai Suburban Railway · CSMT · Kasara · Churchgate · Virar · Panvel
              </p>
            </div>
          </div>

          {/* Right nav */}
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            {/* Corridor pill */}
            <div className="tp-pill tp-pill-white" style={{ display: "none" }} id="corridor-pill-lg">
              <Zap style={{ width: 12, height: 12, color: "var(--c-lime)" }} />
              <span>CORRIDOR: {selectedLine === "ALL" ? "MULTI-LINE" : selectedLine}</span>
            </div>
            <div className="tp-pill tp-pill-white">
              <Zap style={{ width: 12, height: 12, color: "var(--c-lime)" }} />
              <span>CORRIDOR: {selectedLine === "ALL" ? "MULTI" : selectedLine}</span>
            </div>

            {/* Network status dots */}
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              {[
                { label: "CR", color: "#ef4444", glow: "#ef4444" },
                { label: "WR", color: "var(--c-blue)", glow: "var(--c-blue)" },
                { label: "HR", color: "var(--c-lime)", glow: "var(--c-lime)" },
              ].map(({ label, color, glow }) => (
                <div key={label} style={{ display: "flex", alignItems: "center", gap: 5 }}>
                  <span style={{
                    display: "block", width: 6, height: 6, borderRadius: "50%",
                    background: color, boxShadow: `0 0 6px ${glow}`,
                  }} />
                  <span className="tp-label" style={{ color: "var(--c-gray-dim)" }}>{label}</span>
                </div>
              ))}
            </div>

            {/* Config button */}
            <button
              onClick={() => setShowConfig(!showConfig)}
              className="tp-btn tp-btn-dark"
              style={{ gap: 8 }}
            >
              <KeyRound style={{ width: 13, height: 13 }} />
              {showConfig ? "Close" : studentId ? `Roll: ${studentId}` : "Connect DB"}
            </button>
          </div>
        </div>
      </header>

      {/* ── 4. Hero network stats band ── */}
      <div className={`relative z-20 tp-anim-fade ${mounted ? "" : "opacity-0"}`}
        style={{
          background: "linear-gradient(180deg, rgba(4,12,12,0.0) 0%, rgba(4,12,12,0.6) 100%)",
          padding: "32px 24px 0",
        }}
      >
        <div style={{ maxWidth: 1400, margin: "0 auto" }}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 1, background: "rgba(171,255,2,0.06)", border: "1px solid rgba(171,255,2,0.10)", borderRadius: 4 }}>
            {[
              { num: "37", label: "Active Stations", sub: "Kasara Corridor" },
              { num: "98.2%", label: "CR Punctuality", sub: "Central Railway" },
              { num: "99.1%", label: "WR Punctuality", sub: "Western Railway" },
              { num: "v2.5", label: "MCP Engine", sub: "Live Telemetry" },
            ].map(({ num, label, sub }, i) => (
              <div
                key={label}
                className={`tp-anim-up tp-delay-${i + 1}`}
                style={{
                  padding: "20px 24px",
                  borderRight: i < 3 ? "1px solid rgba(171,255,2,0.08)" : undefined,
                }}
              >
                <div className="tp-label" style={{ color: "var(--c-gray-dim)", marginBottom: 6 }}>{sub}</div>
                <div className="tp-stat-number" style={{ fontSize: "1.75rem" }}>{num}</div>
                <div className="tp-label" style={{ color: "var(--c-white-80)", marginTop: 4 }}>{label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── 5. Main Dashboard Content ── */}
      <main style={{ position: "relative", zIndex: 20, maxWidth: 1400, margin: "0 auto", padding: "32px 24px 64px" }}>

        {/* ─ Institute & Profile Selector ─ */}
        <div className={`tp-glass tp-crosshair tp-card-hover tp-anim-up tp-delay-2`}
          style={{ borderRadius: 4, padding: "24px 28px", marginBottom: 24 }}
        >
          {/* Section header */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
            <div className="tp-section-title">
              <Building2 style={{ width: 14, height: 14, color: "var(--c-lime)" }} />
              Institute Database Selection
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span className="tp-label" style={{ color: "var(--c-gray-dim)" }}>Nearest Station:</span>
              <span className="tp-pill tp-pill-lime">{selectedCollege.nearestStation} · {selectedCollege.defaultLine}</span>
            </div>
          </div>

          {/* College pills */}
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 20 }}>
            {MUMBAI_COLLEGES.map((col) => (
              <button
                key={col.id}
                onClick={() => setSelectedCollegeId(col.id)}
                className={`tp-college-pill ${col.id === selectedCollegeId ? "active" : ""}`}
              >
                {col.shortCode}
                <span style={{ opacity: 0.6, marginLeft: 6, fontSize: "0.625rem" }}>
                  {col.location.split(",")[0]}
                </span>
              </button>
            ))}
          </div>

          {/* Divider */}
          <div className="tp-divider" style={{ margin: "16px 0" }} />

          {/* Demo profiles */}
          <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", justifyContent: "space-between", gap: 12 }}>
            <div className="tp-section-title">
              <UserCheck style={{ width: 14, height: 14, color: "var(--c-lime)" }} />
              Student Dataset Profiles
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
              {DEMO_PROFILES.map((p) => {
                const isActive = p.id === activeProfileId;
                const accentColor =
                  p.standingCategory === "borderline" ? "#ffa07a" :
                  p.standingCategory === "critical"   ? "#ff6b6b" :
                  "var(--c-lime)";
                return (
                  <button
                    key={p.id}
                    onClick={() => loadDemoProfile(p.id)}
                    className="tp-profile-card"
                    style={{
                      background: isActive ? "rgba(171,255,2,0.08)" : undefined,
                      borderColor: isActive ? "rgba(171,255,2,0.4)" : undefined,
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <span style={{ width: 6, height: 6, borderRadius: "50%", background: accentColor, flexShrink: 0 }} />
                      <span className="tp-label-lg" style={{ color: isActive ? "var(--c-lime)" : "var(--c-white-80)" }}>
                        {p.name}
                      </span>
                      <span className="tp-label" style={{ color: accentColor, opacity: 0.9 }}>
                        {p.standingCategory}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* ─ Operations Notice Banner ─ */}
        <div className={`tp-anim-up tp-delay-3`} style={{
          display: "flex", alignItems: "center", gap: 20, marginBottom: 28,
          padding: "16px 24px",
          background: "rgba(4,12,12,0.6)",
          border: "1px solid rgba(171,255,2,0.10)",
          borderLeft: "3px solid var(--c-lime)",
          borderRadius: "0 4px 4px 0",
          backdropFilter: "blur(12px)",
        }}>
          <div style={{ flexShrink: 0, display: "flex", alignItems: "center", gap: 10 }}>
            <Radio style={{ width: 16, height: 16, color: "var(--c-lime)" }} />
            <span className="tp-label" style={{ color: "var(--c-lime)" }}>OPS-VERIFIED</span>
          </div>
          <div className="tp-divider" style={{ width: 1, height: 32, background: "rgba(171,255,2,0.12)", flexShrink: 0 }} />
          <div>
            <p className="tp-body" style={{ color: "var(--c-white-80)", fontSize: "0.875rem" }}>
              Central Railway · Kasara Corridor · 37 Stations Topology Active
              <span className="tp-pill tp-pill-lime" style={{ marginLeft: 12, verticalAlign: "middle" }}>
                m-Indicator v2026.09
              </span>
            </p>
            <p className="tp-label" style={{ color: "var(--c-gray-dim)", marginTop: 4 }}>
              Train numbers 95401–95435 Fast · 96402/96406 Slow locals · Live buffer matching active
            </p>
          </div>
          <div style={{ marginLeft: "auto", flexShrink: 0 }}>
            <span className="tp-label-lg" style={{ color: "var(--c-gray-dim)" }}>
              CR-ENG-VERIFIED
            </span>
          </div>
        </div>

        {/* ─ Custom DB Credentials Form ─ */}
        {showConfig && (
          <div className={`tp-glass tp-crosshair tp-anim-up`}
            style={{ borderRadius: 4, padding: "28px", marginBottom: 28, position: "relative", overflow: "hidden" }}
          >
            {/* Top accent line */}
            <div style={{
              position: "absolute", top: 0, left: 0, right: 0, height: 2,
              background: "linear-gradient(90deg, var(--c-lime), rgba(171,255,2,0.3), transparent)",
            }} />

            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24 }}>
              <div>
                <div className="tp-section-title" style={{ marginBottom: 8 }}>
                  <GraduationCap style={{ width: 14, height: 14, color: "var(--c-lime)" }} />
                  Connect College ERP Database
                </div>
                <p className="tp-body" style={{ color: "var(--c-gray-dim)", fontSize: "0.8125rem" }}>
                  Connect your Mumbai University ERP credentials for live attendance sync
                </p>
              </div>
              <span className="tp-pill tp-pill-lime">AES-256 Encrypted</span>
            </div>

            <form onSubmit={handleSave}>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16, marginBottom: 24 }}>
                {[
                  { label: "Student ID / Roll No", placeholder: "241635", type: "text", val: tempId, set: setTempId },
                  { label: "Portal Username", placeholder: "ERP Login", type: "text", val: tempUser, set: setTempUser },
                  { label: "Password", placeholder: "••••••••", type: "password", val: tempPass, set: setTempPass as any },
                ].map(({ label, placeholder, type, val, set }) => (
                  <div key={label}>
                    <label className="tp-label" style={{ color: "var(--c-gray-dim)", display: "block", marginBottom: 8 }}>
                      {label}
                    </label>
                    <input
                      type={type}
                      required
                      value={val}
                      onChange={(e) => (set as any)(e.target.value)}
                      placeholder={placeholder}
                      className="tp-input"
                    />
                  </div>
                ))}
              </div>

              <div className="tp-divider" style={{ marginBottom: 20 }} />

              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--c-lime)" }} />
                  <span className="tp-label" style={{ color: "var(--c-gray-dim)" }}>
                    ACTIVE ADAPTER: {selectedCollege.name} ({selectedCollege.campusCode})
                  </span>
                </div>
                <div style={{ display: "flex", gap: 10 }}>
                  <button type="button" onClick={() => setShowConfig(false)} className="tp-btn tp-btn-ghost">
                    Cancel
                  </button>
                  <button type="submit" className="tp-btn tp-btn-primary">
                    <CheckCircle2 style={{ width: 14, height: 14 }} />
                    Save & Sync Live DB
                  </button>
                </div>
              </div>
            </form>
          </div>
        )}

        {/* ─ Core Dashboard Grid ─ */}
        <div className={`tp-anim-up tp-delay-4`} style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", gap: 24 }}>
          <TrainTrackerCard />
          <AttendanceCard />
        </div>

        {/* ─ Footer ─ */}
        <footer style={{ marginTop: 64, paddingTop: 32, borderTop: "1px solid rgba(171,255,2,0.10)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 16 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
              <img src="/logo.jpg" alt="TransitPulse" style={{ width: 28, height: 28, borderRadius: 6, border: "1px solid rgba(171,255,2,0.2)" }} />
              <span className="tp-label-lg" style={{ color: "var(--c-white-80)" }}>
                Transit<span style={{ color: "var(--c-lime)" }}>Pulse</span>
              </span>
              <div className="tp-divider" style={{ width: 1, height: 16, background: "rgba(255,255,255,0.1)", flexShrink: 0 }} />
              <span className="tp-label" style={{ color: "var(--c-gray-dim)" }}>Autonomous Commute & Campus MCP Engine · v2.5</span>
            </div>
            <div style={{ display: "flex", gap: 20, alignItems: "center" }}>
              {["CR / WR / HR", "37 STATIONS", "KASARA VERIFIED"].map((t) => (
                <span key={t} className="tp-label" style={{ color: "var(--c-gray-dim)" }}>{t}</span>
              ))}
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
};

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Dashboard />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
