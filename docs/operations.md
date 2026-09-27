# Operations & Maintenance Guide

## 1. Starting the Platform

### Local Development
```bash
# Start PostgreSQL & Redis
docker run -d --name tp-postgres -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15-alpine
docker run -d --name tp-redis -p 6379:6379 redis:7-alpine

# Run database migrations / table sync
PYTHONPATH=backend python -c "import asyncio; from app.main import engine, Base; asyncio.run(engine.begin().then(lambda c: c.run_sync(Base.metadata.create_all)))"

# Start FastAPI API server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 2. Health & Readiness Verification

### Liveness Probe
```bash
curl -i http://localhost:8000/health
# HTTP/1.1 200 OK
# {"status": "alive", "timestamp": "2026-09-27T18:00:00Z"}
```

### Readiness Probe
```bash
curl -i http://localhost:8000/ready
# HTTP/1.1 200 OK
# {"status": "ready", "services": {"database": "connected", "redis": "connected"}}
```

---

## 3. Telemetry & Metrics Scrape
```bash
curl -s http://localhost:8000/metrics | grep http_requests_total
```

---

## 4. Background Workers & Schedulers
* **Notification Outbox Dispatcher**: Runs every 10 seconds to sweep `outbox_events` (`status = PENDING`) and generate notifications.
* **Notification Delivery Worker**: Runs every 5 seconds to process `notifications` (`status = PENDING` or `RETRYING`).
* **Class Reminder Scheduler**: Runs every 60 seconds to detect classes starting in 20–35 minutes and emit outbox reminder events.
