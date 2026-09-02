# 🚆 Campus & Commute MCP Server

[![CI Pipeline](https://github.com/httpmonish/MCP-Server-for-Mumbai-Local-Train/actions/workflows/ci.yml/badge.svg)](https://github.com/httpmonish/MCP-Server-for-Mumbai-Local-Train/actions)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?logo=fastapi&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-1.42-2EAD33?logo=playwright&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)
![Model Context Protocol](https://img.shields.io/badge/MCP-Standard-purple)

> A resilient backend data extraction engine, REST API, and Model Context Protocol (MCP) server that liberates student portal records and synchronizes them with Mumbai suburban railway schedules for autonomous LLM reasoning.

---

## 🎯 Problem Statement
University portals frequently lock vital student records (lecture attendance percentages, examination dates, classroom allocations) behind legacy, server-rendered dashboards devoid of public APIs. Concurrently, students commuting via Mumbai's Central and Western railway corridors must manually cross-reference attendance shortfalls against erratic local train timetables.

This project solves this fragmentation by:
1. Automating headless authenticated session scraping with Playwright.
2. Ingesting and parsing official suburban railway timetable PDFs into relational models.
3. Exposing tools via the **Model Context Protocol (MCP)**, allowing AI agents like Claude Desktop to evaluate multi-source queries (e.g., *"Will I reach my 9:00 AM Networks exam on time if I take the next train from Thane?"*).

---

## ⚡ Key Engineering Highlights
- **Cache-Aside Architecture:** Redis-backed caching delivering sub-15ms hits, with deliberate TTL stratification (1 hour for attendance, 24 hours for exams, 12 hours for transit).
- **Graceful Failure Degradation:** Automated fallback pipeline serving historical database state with `stale: true` indicators during upstream portal outages.
- **Defensive Anti-Bot Throttling:** Concurrency semaphores preventing portal hammering, coupled with inbound rate limiting (`slowapi`).
- **Production Containerization:** Hardened Docker build running non-root Playwright Chromium and FastAPI.

---

## 🛠️ Tech Stack
- **Backend:** Python 3.11, FastAPI, SQLAlchemy 2.0, Uvicorn
- **Scraping & Ingestion:** Playwright (Headless Chromium), pdfplumber, Pandas
- **Storage & Caching:** PostgreSQL (Supabase), Redis (Upstash)
- **AI Integration:** Model Context Protocol (MCP) Python SDK
- **Frontend:** HTML5, Modern ES6+ JavaScript, Tailwind CSS (Edge-hosted on Vercel)
- **DevOps & QA:** Docker, GitHub Actions, Pytest, Ruff

---

## 🚀 Quickstart (Local Docker Parity)

### 1. Clone & Configure
```bash
git clone https://github.com/httpmonish/MCP-Server-for-Mumbai-Local-Train.git
cd MCP-Server-for-Mumbai-Local-Train
cp .env.example .env
```

### 2. Launch Stack via Docker Compose

```bash
docker compose -f backend/docker-compose.yml up --build
```

The FastAPI backend will boot on `http://localhost:8000`. Test the health probe:

```bash
curl http://localhost:8000/ready
```

---

## 🤖 Claude Desktop MCP Setup

Add the server to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "campus-commute-server": {
      "command": "/absolute/path/to/venv/bin/python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/absolute/path/to/backend",
      "env": {
        "PYTHONPATH": ".",
        "DATABASE_URL": "postgresql+asyncpg://postgres:postgres@localhost:5432/mcp_production",
        "REDIS_URL": "redis://localhost:6379/0",
        "PORTAL_DEFAULT_USERNAME": "your_student_id",
        "PORTAL_DEFAULT_PASSWORD": "your_password"
      }
    }
  }
}
```

Restart Claude Desktop to use the tools:

* `get_student_attendance`: Retrieve real-time attendance and low-attendance alerts.
* `get_upcoming_exams`: Extract upcoming dates and venues.
* `get_next_train`: Query upcoming local trains between stations.

---

## 📡 REST API Reference

| Method | Endpoint | Description | Rate Limit |
| --- | --- | --- | --- |
| `GET` | `/health` | Liveness probe | Unlimited |
| `GET` | `/ready` | Deep readiness probe (Postgres + Redis check) | Unlimited |
| `POST` | `/api/v1/academic/attendance/{id}` | Fetch student attendance (Cache-Aside + Scraper) | 10 / min |
| `POST` | `/api/v1/academic/exams/{id}` | Fetch scheduled examination timetable | 10 / min |
| `GET` | `/api/v1/trains/next` | Query next suburban trains (`?from_station=X&to_station=Y`) | 30 / min |

---

## 🧪 Running the Test Suite

```bash
# Run all unit, integration, and failure-mode tests
pytest backend/tests/ -v --cov=backend/app
```
