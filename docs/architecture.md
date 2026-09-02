# System Architecture & Technical Specifications: Campus & Commute MCP Server

## 1. System Overview
The Campus & Commute MCP Server automates the extraction, normalization, and contextual delivery of academic records (attendance, examination schedules) and suburban rail transit data. It bridges closed academic portals with modern AI agents via the Model Context Protocol (MCP) and offers a low-latency web dashboard for direct student consumption.

```
+-------------------------------------------------------------------------+
|                              DATA SOURCES                               |
|   +--------------------------+       +------------------------------+   |
|   | College Student Portal   |       | Central / Western Railway    |   |
|   | (Server-Rendered HTML)   |       | Suburban Timetable PDFs      |   |
+---+--------------------------+-------+------------------------------+---+
|                                      |
v                                      v
[Playwright Headless Chrome]            [pdfplumber Tabular Parser]
|                                      |
+-------------------+------------------+
|
v
+---------------------------+
|    ORCHESTRATION LAYER    |
|  (academic_orchestrator)  |
+---------------------------+
|           |
Cache Miss / Write |           | Cache Hit (<15ms)
v           v
+---------------+   +-------------------+
| PostgreSQL    |   | Upstash Redis     |
| (Supabase)    |   | (Cache-Aside)     |
+---------------+   +-------------------+
|                   |
+---------+---------+
|
v
+-------------------------------+
|      FASTAPI BACKEND CORE     |
|  (Rate Limiter, CORS, Router) |
+-------------------------------+
/             \
/               \
v                 v
+--------------------+   +---------------------+
| Model Context      |   | Responsive Web      |
| Protocol (stdio)   |   | Dashboard           |
| [Claude Desktop]   |   | (Vercel Edge Host)  |
+--------------------+   +---------------------+
```

## 2. Core Architectural Principles

### 2.1 Cache-Aside Pattern with Tiered TTLs
- **Attendance Records (`TTL: 3600s / 1 Hour`):** Attendance figures update periodically during academic hours. Redis intercepts repeated queries to protect university servers from IP bans.
- **Exam Timetables (`TTL: 86400s / 24 Hours`):** Examination schedules are static once published.
- **Suburban Train Timetables (`TTL: 43200s / 12 Hours`):** Suburban timetables undergo minor seasonal adjustments, allowing aggressive multi-hour caching partitioned into 10-minute departure windows.

### 2.2 Graceful Degradation & Resilience Matrix
| Failure Scenario | Immediate Detection | System Reaction | User Experience |
| :--- | :--- | :--- | :--- |
| **College Portal Down / HTTP 500** | Playwright timeout / navigation error | Fallback to PostgreSQL `attendance_records` table | Serves cached records with amber warning: `stale: true` |
| **Portal DOM Mutation** | Selector lookup timeout | Raises `PortalSelectorError`, cancels extraction | Prevents dirty data writes; alerts monitoring; serves historical DB state |
| **Upstash Redis Outage** | Connection drop caught in `RedisCache` | Fail-open: bypasses cache and queries PostgreSQL/Scraper directly | Zero API crashes; slight latency increase |
| **Traffic Spike / Scraping Surge** | Concurrency Semaphore saturated (`max=2`) | Enqueues incoming requests; returns 429 via `slowapi` if client threshold exceeded | Prevents university portal server overload and worker memory leaks |

## 3. Engineering Decisions & Trade-offs
1. **Playwright over Raw HTTP Requests:**
   - *Trade-off:* Higher memory and CPU footprint per worker.
   - *Rationale:* Student portals employ dynamic JavaScript DOM mounting, session-based cookie handshakes, and anti-CSRF measures that break simple `requests`/`httpx` pipelines.
2. **Standard I/O (`stdio`) Transport for MCP:**
   - *Trade-off:* Requires local process execution rather than pure cloud SSE endpoints.
   - *Rationale:* Enables zero-friction native integration with Claude Desktop while protecting student credentials within the local environment.
3. **Vanilla ES6+ Frontend over React for v1:**
   - *Trade-off:* Manual DOM manipulation without reactive component state trees.
   - *Rationale:* Eliminates build tools (Vite/Webpack), yields a sub-50KB bundle footprint, and provides instant edge delivery via standard static CDN hosting.
