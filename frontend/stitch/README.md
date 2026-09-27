# मुंबईTeleport — Frontend Section Bifurcation & Backend Synchronization Guide

This folder contains the rectified, bifurcated architectural sections extracted and harmonized from the design system for **मुंबईTeleport (TransitPulse Platform)**.

---

## 1. Bifurcated Sections Breakdown

| Section # | Section Name | React Component (`frontend-v2`) | Backend Synchronized Phase | Key Capabilities & Data Flows |
| :--- | :--- | :--- | :--- | :--- |
| **Section 0** | **Header & Navigation Bar** | [`Header.tsx`](file:///Users/themonishnawaz/Desktop/MCP-Server-for-Mumbai-Local/frontend-v2/src/components/Header.tsx) | **Phase 1 (Auth)** & **Phase 3 (Lines)** | Multi-line switcher (Central Main, Western Line, Harbour, Trans-Harbour), synced headway badge, multi-tenant user profile pill & auth modal trigger. |
| **Section 1** | **Intelligent Route Corridor Selector** | [`CorridorSelector.tsx`](file:///Users/themonishnawaz/Desktop/MCP-Server-for-Mumbai-Local/frontend-v2/src/components/CorridorSelector.tsx) | **Phase 3 (Transit Engine)** & **Phase 4 (Schedules)** | Origin station selector (e.g. Thane `[TNA]` PF 5), direction swap capsule, destination campus/office hub (e.g. Matunga / Dadar `[DR]` VJTI), and Fast rake search filter. |
| **Section 2** | **TMS Vector Block Clearance Map (Visual Stepper)** | [`BlockClearanceMap.tsx`](file:///Users/themonishnawaz/Desktop/MCP-Server-for-Mumbai-Local/frontend-v2/src/components/BlockClearanceMap.tsx) | **Phase 3 (Topology & Live Provider)** | Curvilinear SVG track corridor (Thane ➔ Ghatkopar ➔ Kurla Junction ➔ Dadar ➔ CSMT), dual-amber caution signals, and glowing live rake beacon (#95401 FAST @ 92 km/h). |
| **Section 3** | **Today's Flow (Down Local / Fast Telemetry Cards)** | [`LiveRakeList.tsx`](file:///Users/themonishnawaz/Desktop/MCP-Server-for-Mumbai-Local/frontend-v2/src/components/LiveRakeList.tsx) | **Phase 3 (Trains)** & **Phase 4 (Today / Week)** | Live train arrival/departure timings, 12-car rake profiles, arrival buffer before scheduled lectures, and expandable coach-by-coach crowding density matrix (General, FC, Ladies, Divyang). |
| **Section 4** | **VJTI / Corporate Attendance & Debarment Radar** | [`AttendanceRadar.tsx`](file:///Users/themonishnawaz/Desktop/MCP-Server-for-Mumbai-Local/frontend-v2/src/components/AttendanceRadar.tsx) | **Phase 5 (Attendance Engine & Shortage Policy)** | Radial circular percentage gauge (e.g. 74.3% vs 75.0% statutory threshold), debarment alert for 09:30 DBMS lecture, contingency sprint protocol, and verified delay slip generation. |
| **Section 5** | **Suburban Core Telemetry** | [`CoreTelemetry.tsx`](file:///Users/themonishnawaz/Desktop/MCP-Server-for-Mumbai-Local/frontend-v2/src/components/CoreTelemetry.tsx) | **Phase 0 & Phase 3 Telemetry** | Active rakes count (128 rakes), 25 kV AC OHE traction health, and live terminal inflow stress gauges (Dadar 94%, Kurla 82%, Thane 88%). |
| **Section 6** | **Live TMS Dispatch Stream** | [`DispatchStream.tsx`](file:///Users/themonishnawaz/Desktop/MCP-Server-for-Mumbai-Local/frontend-v2/src/components/DispatchStream.tsx) | **Phase 3 (Live Scraper / Provider)** | Chronological dispatch feed directly from Mumbai CSMT / Kalyan control rooms (Platform clearances, speed restrictions, AC rake shed sync). |
| **Section 7** | **Multi-Tenant Auth & Org Modal** | [`AuthModal.tsx`](file:///Users/themonishnawaz/Desktop/MCP-Server-for-Mumbai-Local/frontend-v2/src/components/AuthModal.tsx) | **Phase 1 (Auth)** & **Phase 2 (Orgs)** | User login, JWT token management, Organization creation (College / Company / Hotel), and RBAC switching (Student, Employee, Teacher, Admin). |

---

## 2. Directory Structure in `frontend/stitch/`

```text
frontend/stitch/
├── README.md                          # Architecture & synchronization documentation
├── dashboard.html                     # Full standalone responsive HTML5 dashboard
└── sections/
    ├── 1_corridor_selector.html       # Origin/Destination corridor swapping widget
    ├── 2_block_clearance_map.html     # SVG vector block clearance track map
    ├── 3_today_flow_rakes.html        # Today's flow cards & coach density drawer
    ├── 4_attendance_radar.html        # Biometric attendance & shortage contingency radar
    ├── 5_core_telemetry.html          # Network power, rakes & terminal stress gauges
    └── 6_dispatch_stream.html         # Live TMS train movement dispatch log
```
