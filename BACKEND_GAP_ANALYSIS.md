# Mumbai Suburban Flow & MCP Telemetry: Bidirectional Gap Analysis Report

## Executive Summary
This document logs the bidirectional architectural gap between the stitched frontend visualization interface ("मुंबईTeleport") and the production TransitPulse backend platform.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       MUMBAI SUBURBAN FLOW ENGINE                           │
├──────────────────────────────────────┬──────────────────────────────────────┤
│  CATEGORY A: UI Built, Needs Backend │  CATEGORY B: Backend Ready, Needs UI │
│  (Frontend Present, Backend Missing) │  (Backend Available, UI Missing)     │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ • Coach-by-Coach Real-Time Crowding  │ • Sunday Mega Block / Jumbo Block    │
│ • Automatic College ERP Attendance   │ • Fast/Slow Track Crossover Signals  │
│ • Cryptographic SHA-256 Delay Slip   │ • 12-Car vs 15-Car Platform Markers  │
│ • Biometric Turnstile Machine Sync   │ • Motorman Cab Audio / Emergency Msg │
│ • Cabin HVAC Live Temperature Sensor │ • Harbour Line Wadala Loop Reroute   │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

---

## Category A: Frontend Rendered, Backend Missing (API Requirements)

1. **Coach-by-Coach Real-Time Crowding Matrix**:
   - *Current Frontend*: Renders individual percentages for Coaches 1–12 (Ladies, First Class, General) with FOB alignment hints.
   - *Backend Need*: Requires bogie suspension pressure transducer ingestion or optical AI crowd counting from platform CCTV feeds. Currently simulated via `coachMatrix` in `telemetryService.ts`.

2. **College Biometric Turnstile Integration**:
   - *Current Frontend*: Displays "Biometric Machine #04 Closes 09:30 AM" and automatic shortage warnings.
   - *Backend Need*: Webhook synchronization with college ERPs (e.g. VJTI ERP, SPIT MIS) to pull live punch-in events.

3. **Cryptographic Central Railway Delay Token**:
   - *Current Frontend*: Generates digital delay certificates with SHA-256 digests and HOD email dispatch.
   - *Backend Need*: Official Central Railway / Western Railway TMS API signing key pair for verification.

4. **Medha AC Rake IoT Temperature Telemetry**:
   - *Current Frontend*: Displays live cabin temperature (`21.0°C`).
   - *Backend Need*: Rolling stock IoT telemetry gateway.

---

## Category B: Backend Capable, Frontend Missing (UI Expansion Opportunities)

1. **Sunday Mega Block & Jumbo Block Visualizer**:
   - *Backend Capacity*: PostgreSQL transit maintenance records track scheduled block occupations between Matunga & Mulund / Borivali & Goregaon.
   - *UI Opportunity*: Route bypass visualizer on the SVG track topology.

2. **Kurla / Vidyavihar Fast-Slow Crossover Switch Points**:
   - *Backend Capacity*: Route topology records tracks 1, 2 (Slow) and 3, 4 (Fast) with crossover speed limits (30 km/h).
   - *UI Opportunity*: Interactive switch point animation on track deviation events.

3. **12-Car vs 15-Car Platform Marker Indicator**:
   - *Backend Capacity*: Station platform lengths and train coach composition models.
   - *UI Opportunity*: Visual platform docking diagram showing where the train will stop on the platform.

4. **Harbour Line Wadala Interchange Loop**:
   - *Backend Capacity*: Multi-line network graph supporting CSMT-Panvel and Churchgate-Goregaon interchange paths.
   - *UI Opportunity*: Interactive multi-leg route recommendations.
