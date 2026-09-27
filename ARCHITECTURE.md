# TransitPulse Platform — Complete System Architecture

## 1. High-Level Modular Architecture

```text
                           CLIENTS & MCP AGENTS
                       (Web, Mobile, Claude, Cursor)
                                     │
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        FASTAPI REST & MCP LAYER                        │
│  - Observability & Security Middleware (X-Request-ID, X-Trace-ID)      │
│  - Standardized Error Handling & Rate Limiting (SlowAPI)               │
│  - JWT Bearer Authentication & Multi-Tenant Scoping                    │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       MODULAR APPLICATION SERVICES                     │
│  ┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐  │
│  │   Auth & Tenant    │ │  Schedule Engine   │ │ Attendance Engine  │  │
│  │   (Phase 1 & 2)    │ │     (Phase 4)      │ │     (Phase 5)      │  │
│  └────────────────────┘ └────────────────────┘ └────────────────────┘  │
│  ┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐  │
│  │   Transit Engine   │ │ Commute & Decision │ │    MCP Gateway     │  │
│  │     (Phase 3)      │ │     (Phase 6)      │ │     (Phase 7)      │  │
│  └────────────────────┘ └────────────────────┘ └────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │             Notification Engine & Transactional Outbox           │  │
│  │                             (Phase 8)                            │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    ▼                                 ▼
┌────────────────────────────────────────┐ ┌─────────────────────────────┐
│          POSTGRESQL (Asyncpg)          │ │        REDIS (aioredis)     │
│  - Organizations & User Accounts       │ │  - Refresh Token Sessions   │
│  - Schedules, Slots & Exceptions       │ │  - Transit Timetable Cache  │
│  - Attendance Records & Policies       │ │  - Rate Limiter Buckets     │
│  - Transactional Outbox & Deliveries   │ │  - Ephemeral Delay Feeds    │
└────────────────────────────────────────┘ └─────────────────────────────┘
```

---

## 2. Core Subsystems

### 2.1 Identity & Multi-Tenancy (Phases 1 & 2)
* Organization boundaries are enforced by scoping all records to `org_id`.
* User hierarchy: `PLATFORM_ADMIN` $\rightarrow$ `ORG_ADMIN` $\rightarrow$ `TEACHER` / `HR_ADMIN` $\rightarrow$ `STUDENT` / `EMPLOYEE`.
* Refresh tokens are stored hashed (SHA-256) in Redis with single-use rotation.

### 2.2 Mumbai Transit Data Pipeline (Phase 3)
* Static timetable database for Mumbai suburban railway (Central, Western, Harbour lines).
* Upstream real-time provider adapter (`RailRadarProvider`, `MockTransitProvider`).
* Automatic degraded fallback: if live providers fail or report stale telemetry ($>180$s), the system seamlessly returns cached static timetables with explicit metadata (`data_label: STATIC_TIMETABLE`, `is_live: false`).

### 2.3 Schedule & Timetable Engine (Phase 4)
* Recurring class schedules and employee shifts with day-of-week slots, campus locations, and nearest station codes.
* Exception management: `ScheduleException` model handles holidays and class cancellations.

### 2.4 Attendance Engine (Phase 5)
* Configurable minimum percentage thresholds per role.
* Authoritative session-by-session records (`PRESENT`, `ABSENT`, `LATE`, `EXCUSED`).
* Immutable audit trail for corrections (`AttendanceAudit`).

### 2.5 Commute & Attendance Intelligence Engine (Phase 6)
* 100% deterministic decision logic combining schedule times, transit travel times, walking margins, and attendance percentages.
* Classifies commute into: `NORMAL`, `AT_RISK`, `LIKELY_LATE`, `STALE_DATA`, `NO_DATA`.

### 2.6 Read-Only Model Context Protocol Server (Phase 7)
* Secure bridge exposing read-only tools (`get_my_schedule`, `get_attendance_summary`, `get_next_train`, `check_commute_risk`) to MCP-compatible AI hosts without compromising multi-tenant authorization.

### 2.7 Production Notification & Alerting Engine (Phase 8)
* Transactional Outbox pattern guarantees no alert is lost if a domain transaction commits.
* Database-level deduplication prevents duplicate emails during retries or concurrent worker runs.
* Timezone-aware quiet hours and user opt-out preferences.

### 2.8 Observability & Reliability (Phase 9)
* Structured JSON logs with correlation IDs (`request_id`, `trace_id`).
* Prometheus `/metrics` endpoint with low-cardinality telemetry across all layers.
* Automated Sentry error capture with sensitive PII and authorization header scrubbing.
