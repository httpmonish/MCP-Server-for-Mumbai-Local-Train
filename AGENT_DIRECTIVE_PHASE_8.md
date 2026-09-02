# AGENT DIRECTIVE: Phase 8 — Recruiter Polish, Production Documentation, CI/CD & Test Automation

You are a principal software engineer and open-source tech lead. Implement Phase 8 of the `mcp-data-server`. Your objective is to harden the codebase for high-signal recruitment review and open-source contribution: build an automated GitHub Actions CI pipeline, produce comprehensive technical architecture documentation with ASCII/Mermaid flowcharts, generate a recruiter-grade README detailing key engineering trade-offs, and construct an automated end-to-end regression demonstration test suite.

Every file below must be written in full production quality. Do not use placeholders, generic descriptions, or dummy stubs.

---

## 1. ENVIRONMENT & DEPENDENCIES
Ensure testing, linting, and coverage utilities are installed in the backend environment:
```bash
pip install ruff pytest pytest-asyncio pytest-cov httpx
```

---

## 2. FILE-BY-FILE PRODUCTION SPECIFICATIONS

### File 1: `.github/workflows/ci.yml`

Implement a continuous integration workflow executing on every push and pull request to `main`:

```yaml
name: CI Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  audit-and-test:
    name: Lint, Test & Coverage
    runs-on: ubuntu-latest
    timeout-minutes: 15

    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres_password
          POSTGRES_DB: mcp_test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - name: Checkout Source Code
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install Python Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r backend/requirements.txt
          pip install ruff pytest pytest-asyncio pytest-cov httpx

      - name: Install Playwright Chromium & System Dependencies
        run: |
          playwright install chromium --with-deps

      - name: Static Code Analysis (Ruff Linter)
        run: |
          ruff check backend/

      - name: Execute Pytest Suite with Coverage
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres_password@localhost:5432/mcp_test_db
          REDIS_URL: redis://localhost:6379/0
          PORTAL_BASE_URL: https://portal-mock.internal
          PYTHONPATH: backend
        run: |
          pytest backend/tests/ -v --cov=backend/app --cov-report=xml --cov-report=term-missing

      - name: Upload Test Coverage Artifact
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: coverage.xml
          retention-days: 7
```

### File 2: `docs/architecture.md`

Write an exhaustive technical architecture document detailing system mechanics, data flows, and design rationale:

```markdown
# System Architecture & Technical Specifications: Campus & Commute MCP Server

## 1. System Overview
The Campus & Commute MCP Server automates the extraction, normalization, and contextual delivery of academic records (attendance, examination schedules) and suburban rail transit data. It bridges closed academic portals with modern AI agents via the Model Context Protocol (MCP) and offers a low-latency web dashboard for direct student consumption.

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
```

### File 3: `README.md`

Produce an executive-level, recruiter-facing project README.

### File 4: `backend/tests/test_recruiter_demo.py`
Create an automated test demonstrating the full lifecycle (caching, scraping fallback, train queries, and MCP formatting):
```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.academic_orchestrator import AcademicOrchestrator
from app.mcp_server.formatters import format_attendance_report, format_train_schedule
from app.scrapers.exceptions import PortalTimeoutError

@pytest.mark.asyncio
async def test_full_degradation_pipeline_and_formatting():
    # 1. Setup mocks
    mock_scraper = MagicMock()
    mock_scraper.login = AsyncMock(side_effect=PortalTimeoutError("Portal offline"))
    mock_cache = MagicMock()
    mock_cache.get = AsyncMock(return_value=None)  # Cache miss

    # Mock historical database data
    mock_db = MagicMock()
    mock_record = MagicMock()
    mock_record.subject_name = "Advanced Computer Networks"
    mock_record.total_conducted = 40
    mock_record.total_attended = 28
    mock_record.percentage = 70.0
    mock_record.last_synced_at.isoformat.return_value = "2026-10-01T08:00:00Z"
    
    # 2. Test orchestrator fallback to DB
    orchestrator = AcademicOrchestrator(
        scraper=mock_scraper,
        cache=mock_cache,
        db_session_factory=lambda: mock_db
    )
    orchestrator._query_db_attendance = AsyncMock(return_value=[{
        "subject_name": mock_record.subject_name,
        "total_conducted": mock_record.total_conducted,
        "total_attended": mock_record.total_attended,
        "percentage": mock_record.percentage,
        "last_synced_at": "2026-10-01T08:00:00Z"
    }])

    result = await orchestrator.get_attendance("241635", {"username": "u", "password": "p"})
    
    assert result["source"] == "database"
    assert result["stale"] is True
    
    # 3. Test MCP text output formatting with critical warning badge
    formatted_report = format_attendance_report("241635", result)
    assert "[WARNING: UPSTREAM PORTAL UNREACHABLE" in formatted_report
    assert "CRITICAL WARNING (<75%)" in formatted_report
    assert "Advanced Computer Networks" in formatted_report

def test_train_mcp_formatting():
    mock_trains = [{
        "train_number": "95701",
        "line": "CR",
        "train_type": "FAST",
        "departure_from_source": "08:22",
        "arrival_at_destination": "08:58",
        "travel_time_minutes": 36
    }]
    output = format_train_schedule("Thane", "Byculla", mock_trains)
    assert "| 95701 | CR | FAST | 08:22 | 08:58 | 36 mins |" in output
```

### File 5: `docs/demo_script.md`

Provide a structured walkthrough script for recording a portfolio presentation video or recruiter screen share.

---

## 3. VERIFICATION & AUDIT COMMANDS

Run the complete testing and static code analysis suite:

```bash
# 1. Run Ruff linter across the backend codebase
ruff check backend/

# 2. Run the full test suite including recruiter demo integration tests
pytest backend/tests/ -v --cov=backend/app

# 3. Verify git cleanliness before release
git status
```
