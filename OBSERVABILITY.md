# TransitPulse Observability & Telemetry Architecture

## 1. Observability Pillars
TransitPulse implements the three core observability signals:
1. **Structured JSON Logs**: Machine-readable JSON logs bound with `request_id`, `trace_id`, execution duration, and automatic regex redaction of passwords, tokens, and authorization headers.
2. **Prometheus Metrics**: Exposes low-cardinality Prometheus telemetry on `/metrics` measuring HTTP request count, latencies (p50, p95, p99), database queries, Redis hit/miss rates, transit provider calls, outbox queues, MCP tool calls, and security events.
3. **Correlation Traces**: Every request generates or propagates an `X-Request-ID` and `X-Trace-ID` across middleware, database transactions, background workers, and MCP server invocations.

## 2. Telemetry Endpoints
- `GET /metrics`: Standard Prometheus metrics endpoint for Grafana/Datadog scraping.
- `GET /health`: Liveness probe ensuring the FastAPI process is responsive.
- `GET /ready`: Readiness probe verifying PostgreSQL connection pool and Redis cache connectivity before routing traffic.

For deep dive details and sample log payloads, see [docs/observability.md](docs/observability.md).
