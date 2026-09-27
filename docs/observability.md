# Observability Architecture & Telemetry Dictionary

## 1. Overview
TransitPulse implements a three-pillar observability framework consisting of:
1. **Structured JSON Logging** with ContextVars-based Request & Trace correlation and automated secret/PII redaction.
2. **Prometheus-Compatible Metrics** (`/metrics`) covering HTTP, Database, Redis Cache, Upstream Transit Providers, Notifications, MCP Server, and Security events.
3. **OpenTelemetry Trace Correlation** generating 128-bit trace identifiers (`X-Trace-ID`) propagated through HTTP responses and downstream worker tasks.
4. **Sentry Error Tracking** with client-side header/cookie scrubbing and release tracking.

---

## 2. Structured JSON Log Schema
Every log entry emitted by the backend is serialized into JSON with the following structure:
```json
{
  "timestamp": "2026-09-27T18:09:47.545203+00:00",
  "level": "INFO",
  "logger": "core.middleware",
  "message": "HTTP GET /api/v1/notifications/me -> 200 (12.4ms)",
  "service": "मुंबईTeleport Platform",
  "environment": "production",
  "request_id": "req_48f286f42022405b",
  "trace_id": "trc_ba23884f19ad40bc9cd2dd7092a5d2ec",
  "user_id": "usr_930049b4-a195-40c6-b355-2621e7ffd6fd",
  "org_id": "org_28f2a8a4-af53-4a4f-98bf-6e768a4e0dab",
  "method": "GET",
  "path": "/api/v1/notifications/me",
  "status_code": 200,
  "duration_ms": 12.4
}
```

### PII & Secret Redaction Policy
The `SecretRedactionFilter` and `redact_dict` functions automatically scrub the following tokens and replace them with `[REDACTED]`:
* `password`, `password_hash`, `plaintext_password`
* `authorization` headers and `Bearer` JWT access/refresh tokens
* `api_key`, `secret_key`, `jwt_secret_key`
* `notification_sendgrid_api_key`, `railradar_api_key`

---

## 3. Prometheus Metrics Catalog

| Metric Name | Type | Labels | Description |
| :--- | :--- | :--- | :--- |
| `http_requests_total` | Counter | `method`, `route`, `status_code` | Total HTTP requests handled |
| `http_request_duration_seconds` | Histogram | `method`, `route`, `status_code` | HTTP request latency percentiles (p50, p95, p99) |
| `db_query_duration_seconds` | Histogram | `operation`, `table` | Database latency in seconds |
| `db_errors_total` | Counter | `error_type` | Total database exceptions |
| `cache_operations_total` | Counter | `operation`, `status` | Redis cache lookups (hit/miss) |
| `transit_provider_requests_total` | Counter | `provider`, `status` | Upstream live transit provider API queries |
| `transit_provider_latency_seconds` | Histogram | `provider` | Transit provider latency |
| `transit_provider_errors_total` | Counter | `provider`, `error_type` | Transit provider timeout/5xx failures |
| `transit_data_freshness_seconds` | Gauge | `line_or_station` | Age of latest live train telemetry observation |
| `notification_events_total` | Counter | `event_type`, `status` | Domain events recorded to Outbox |
| `notification_deliveries_total` | Counter | `channel`, `provider`, `status` | Notification delivery attempts |
| `notification_delivery_latency_seconds`| Histogram | `channel`, `provider` | Email/push delivery duration |
| `notification_retries_total` | Counter | `channel`, `error_code` | Delivery retries scheduled |
| `notification_suppressed_total` | Counter | `reason` | Notifications suppressed (quiet hours, opt-out) |
| `mcp_tool_calls_total` | Counter | `tool_name`, `status` | Model Context Protocol tool calls |
| `mcp_tool_duration_seconds` | Histogram | `tool_name` | MCP tool execution duration |
| `mcp_tool_errors_total` | Counter | `tool_name`, `error_code` | MCP tool failures |
| `security_events_total` | Counter | `event_type`, `severity` | Security threats (unauthorized, rate limits, IDOR attempts) |

---

## 4. SLOs (Service Level Objectives) & SLIs

### SLI 1: API Availability
$$\text{Availability} = \frac{\sum \text{http\_requests\_total}\{\text{status\_code}!=\text{"5xx"}\}}{\sum \text{http\_requests\_total}} \ge 99.9\%$$

### SLI 2: P95 HTTP Latency
$$\text{P95 Latency for Read Routes} \le 150\text{ms}$$
$$\text{P95 Latency for Intelligence Engine Routes} \le 350\text{ms}$$

### SLI 3: Live Transit Freshness
$$\text{transit\_data\_freshness\_seconds} \le 120\text{s}$$
*(If freshness $> 180\text{s}$, automatically fall back to static timetables with degraded flag).*
