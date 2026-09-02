# AGENT DIRECTIVE: Phase 10 — Autonomous Background Worker Engine, Proactive Commute Alerts & Observability

You are a principal backend infrastructure and distributed systems engineer. Implement Phase 10 of the `mcp-data-server`. Your objective is to build an event-driven background task processing engine using Redis Streams / ARQ, a cron-based proactive commuter alert system delivering daily morning briefings via Telegram Bot API and WebPush, an autonomous trip-recommendation decision algorithm that correlates attendance deficits with scheduled train arrivals, and a production observability layer exporting Prometheus metrics and OpenTelemetry traces.

Every file below must be written in full production quality. Do not use placeholders, dummy print statements, or omitted error handling.

---

## 1. ENVIRONMENT & DEPENDENCIES
Install the required asynchronous task processing, alerting, and observability packages:
```bash
pip install arq prometheus-client opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi python-telegram-bot httpx
```

---

## 2. FILE-BY-FILE PRODUCTION SPECIFICATIONS

### File 1: `backend/app/core/telemetry.py`

Configure structured Prometheus instrumentation to monitor scraper efficiency, cache hit ratios, and background jobs.

* **Imports**: `from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST`.
* **Metrics Definitions**:
  * `SCRAPER_EXECUTION_TIME = Histogram("scraper_duration_seconds", "Time spent running Playwright portal scraper", ["status", "target"], buckets=[1.0, 3.0, 5.0, 10.0, 20.0, 30.0])`
  * `SCRAPER_FAILURES_TOTAL = Counter("scraper_failures_total", "Total scraper failures categorized by exception", ["exception_type"])`
  * `CACHE_OPERATIONS_TOTAL = Counter("cache_operations_total", "Redis cache lookups", ["operation", "status"])`
  * `ACTIVE_SCRAPER_WORKERS = Gauge("active_scraper_workers", "Number of currently executing Playwright browser contexts")`
  * `ALERTS_DISPATCHED_TOTAL = Counter("alerts_dispatched_total", "Total proactive notifications sent", ["channel", "status"])`

* **Helper Functions**:
  * `def record_cache_hit(key_prefix: str) -> None`: Increments `CACHE_OPERATIONS_TOTAL.labels(operation=key_prefix, status="hit")`.
  * `def record_cache_miss(key_prefix: str) -> None`: Increments `CACHE_OPERATIONS_TOTAL.labels(operation=key_prefix, status="miss")`.
  * `def get_metrics_payload() -> tuple[bytes, str]`: Returns `(generate_latest(), CONTENT_TYPE_LATEST)`.

### File 2: `backend/app/services/alert_service.py`

Implement a multi-channel dispatcher sending rich notification cards to students via Telegram Bot API and HTTP Webhooks.

* **Imports**: `httpx`, `app.core.config.settings`, `app.core.logger.get_logger`, `app.core.telemetry.ALERTS_DISPATCHED_TOTAL`.
* **Class `AlertDispatcher`**:
  * `__init__(self, telegram_bot_token: Optional[str] = None, telegram_chat_id: Optional[str] = None)`:
    * Initialize HTTPX async client with a 10-second timeout.
  * `async def send_telegram_alert(self, message_markdown: str) -> bool`:
    * Endpoint: `https://api.telegram.org/bot{token}/sendMessage`.
    * Payload: `{"chat_id": chat_id, "text": message_markdown, "parse_mode": "MarkdownV2", "disable_web_page_preview": True}`.
    * Escape special MarkdownV2 characters (`_`, `*`, `[`, `]`, `(`, `)`, `~`, `>`, `#`, `+`, `-`, `=`, `|`, `{`, `}`, `.`, `!`).
    * On HTTP 200: Increment `ALERTS_DISPATCHED_TOTAL.labels(channel="telegram", status="success")`, return `True`.
    * On failure: Log error, increment `ALERTS_DISPATCHED_TOTAL.labels(channel="telegram", status="failure")`, return `False`.
  * `async def send_webhook_alert(self, webhook_url: str, payload: dict) -> bool`:
    * Dispatch POST request with JSON payload to custom user webhook (Discord, Slack, or local listener).
    * Handle network errors gracefully without crashing the worker.

### File 3: `backend/app/services/decision_engine.py`

Implement an autonomous reasoning engine that correlates academic urgency against transit arrival buffers.

* **Imports**: `datetime.datetime`, `datetime.time`, `datetime.timedelta`, `typing.Dict`, `typing.Any`, `typing.List`.
* **Class `CommuteDecisionEngine`**:
  * **Method `evaluate_commute_urgency(attendance_records: List[Dict], exam_records: List[Dict], available_trains: List[Dict], target_arrival_time: time) -> Dict[str, Any]`**:
    1. **Analyze Academic Risk:**
       * Identify subjects with `percentage < 75.0%`.
       * Check if an exam is scheduled for today (`exam_date == today`).
       * Compute risk level:
         * `HIGH`: Exam scheduled today OR multiple subjects `< 70.0%`.
         * `MEDIUM`: 1 or 2 subjects between `70.0%` and `74.9%`.
         * `LOW`: All subjects $\ge 75.0\%$, no exams today.
    2. **Transit Buffer Matching:**
       * Iterate through `available_trains`.
       * Parse `arrival_at_destination` into datetime.
       * Calculate arrival margin: `buffer_minutes = (target_arrival_time - arrival_time).total_seconds() / 60`.
       * Determine the optimal train:
         * For `HIGH` risk: Select the train arriving with $\ge 25$ minutes buffer (accounts for railway delays).
         * For `MEDIUM` risk: Select the train arriving with $\ge 15$ minutes buffer.
         * For `LOW` risk: Select the train arriving with $\ge 5$ minutes buffer.
    3. **Generate Actionable Briefing:**
       * Return dictionary with `risk_level`, `recommended_train`, `backup_train`, `urgency_reason`, and `warning_subjects`.

### File 4: `backend/app/worker/tasks.py`

Implement asynchronous background worker functions executed by the `arq` worker process.

* **Imports**: `arq.Retry`, `app.services.academic_orchestrator.AcademicOrchestrator`, `app.services.train_service.TrainService`, `app.services.decision_engine.CommuteDecisionEngine`, `app.services.alert_service.AlertDispatcher`.
* **Task `task_morning_commute_digest(ctx, student_id: str, username: str, password: str, source_station: str, destination_station: str, target_lecture_time: str, telegram_chat_id: str)`**:
  1. Retrieve student attendance using `AcademicOrchestrator.get_attendance()`.
  2. Retrieve student exams using `AcademicOrchestrator.get_exams()`.
  3. Query upcoming suburban trains departing after 07:00 AM using `TrainService.get_next_trains()`.
  4. Pass data into `CommuteDecisionEngine.evaluate_commute_urgency()`.
  5. Format structured markdown notification:
  6. Dispatch via `AlertDispatcher.send_telegram_alert()`.
* **Task `task_background_cache_warm(ctx, stations_pair: List[tuple])`**:
  * Run every 30 minutes during peak hours (07:00–11:00 AM, 16:00–20:00 PM).
  * Pre-fetch next trains for common routes (e.g., Thane $\to$ Byculla, CSMT $\to$ Kalyan) and populate Redis to guarantee sub-millisecond cache hits for interactive users.

### File 5: `backend/app/worker/worker.py`

Configure the `arq` worker process and cron schedules.

* **Imports**: `arq.cron`, `arq.connections.RedisSettings`, `app.core.config.settings`, `app.worker.tasks.*`.
* **Cron Jobs Configuration**:
  * Run `task_morning_commute_digest` Monday through Saturday at 07:15 AM IST (`hour=1, minute=45` UTC):
    * `cron(task_morning_commute_digest, hour={1}, minute={45}, run_at_startup=False)`
  * Run `task_background_cache_warm` every 15 minutes:
    * `cron(task_background_cache_warm, minute={0, 15, 30, 45})`
* **Worker Settings Class `WorkerSettings`**:
  * `functions = [task_morning_commute_digest, task_background_cache_warm]`
  * `cron_jobs = [...]`
  * `redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)`
  * `max_jobs = 10`
  * `job_timeout = 120`

### File 6: `backend/app/routes/metrics.py`

Expose the Prometheus scraping endpoint on the FastAPI app.

* **Imports**: `fastapi.APIRouter`, `fastapi.responses.Response`, `app.core.telemetry.get_metrics_payload`.
* Router prefix: `/metrics`.
* **Endpoint `GET /`**:
  * Call `get_metrics_payload()`.
  * Return `Response(content=body, media_type=content_type)`.

---

## 3. UNIT & INTEGRATION TEST SPECIFICATIONS

### File 7: `backend/tests/test_decision_engine.py`
### File 8: `backend/tests/test_alert_dispatcher.py`
### File 9: `backend/tests/test_metrics_endpoint.py`

---

## 4. VERIFICATION COMMANDS

Execute test suites and verify worker startup:
```bash
pytest backend/tests/test_decision_engine.py backend/tests/test_alert_dispatcher.py backend/tests/test_metrics_endpoint.py -v
python -m arq app.worker.worker.WorkerSettings --check
```
