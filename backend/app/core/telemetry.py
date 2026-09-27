from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

# ------------------------------------------------------------------------------
# 1. HTTP REQUEST METRICS
# ------------------------------------------------------------------------------
if "http_requests_total" in REGISTRY._names_to_collectors:
    HTTP_REQUESTS_TOTAL = REGISTRY._names_to_collectors["http_requests_total"]
else:
    HTTP_REQUESTS_TOTAL = Counter(
        "http_requests_total",
        "Total number of HTTP requests handled by the FastAPI application",
        ["method", "route", "status_code"],
    )

if "http_request_duration_seconds" in REGISTRY._names_to_collectors:
    HTTP_REQUEST_DURATION = REGISTRY._names_to_collectors["http_request_duration_seconds"]
else:
    HTTP_REQUEST_DURATION = Histogram(
        "http_request_duration_seconds",
        "HTTP request latency in seconds",
        ["method", "route", "status_code"],
        buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
    )

# ------------------------------------------------------------------------------
# 2. DATABASE & REDIS CACHE METRICS
# ------------------------------------------------------------------------------
if "db_query_duration_seconds" in REGISTRY._names_to_collectors:
    DB_QUERY_DURATION = REGISTRY._names_to_collectors["db_query_duration_seconds"]
else:
    DB_QUERY_DURATION = Histogram(
        "db_query_duration_seconds",
        "Database query duration in seconds",
        ["operation", "table"],
        buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 3.0],
    )

if "db_errors_total" in REGISTRY._names_to_collectors:
    DB_ERRORS_TOTAL = REGISTRY._names_to_collectors["db_errors_total"]
else:
    DB_ERRORS_TOTAL = Counter(
        "db_errors_total",
        "Total database errors encountered",
        ["error_type"],
    )

if "cache_operations_total" in REGISTRY._names_to_collectors:
    CACHE_OPERATIONS_TOTAL = REGISTRY._names_to_collectors["cache_operations_total"]
else:
    CACHE_OPERATIONS_TOTAL = Counter(
        "cache_operations_total",
        "Redis cache lookups and mutations",
        ["operation", "status"],
    )

# ------------------------------------------------------------------------------
# 3. TRANSIT PROVIDER & TIMETABLE METRICS
# ------------------------------------------------------------------------------
if "transit_provider_requests_total" in REGISTRY._names_to_collectors:
    TRANSIT_PROVIDER_REQUESTS_TOTAL = REGISTRY._names_to_collectors["transit_provider_requests_total"]
else:
    TRANSIT_PROVIDER_REQUESTS_TOTAL = Counter(
        "transit_provider_requests_total",
        "Total requests made to upstream transit data providers",
        ["provider", "status"],
    )

if "transit_provider_latency_seconds" in REGISTRY._names_to_collectors:
    TRANSIT_PROVIDER_LATENCY = REGISTRY._names_to_collectors["transit_provider_latency_seconds"]
else:
    TRANSIT_PROVIDER_LATENCY = Histogram(
        "transit_provider_latency_seconds",
        "Latency of upstream transit provider API calls",
        ["provider"],
        buckets=[0.1, 0.25, 0.5, 1.0, 2.0, 3.5, 5.0, 10.0],
    )

if "transit_provider_errors_total" in REGISTRY._names_to_collectors:
    TRANSIT_PROVIDER_ERRORS_TOTAL = REGISTRY._names_to_collectors["transit_provider_errors_total"]
else:
    TRANSIT_PROVIDER_ERRORS_TOTAL = Counter(
        "transit_provider_errors_total",
        "Errors encountered during transit data fetching and normalization",
        ["provider", "error_type"],
    )

if "transit_data_freshness_seconds" in REGISTRY._names_to_collectors:
    TRANSIT_DATA_FRESHNESS = REGISTRY._names_to_collectors["transit_data_freshness_seconds"]
else:
    TRANSIT_DATA_FRESHNESS = Gauge(
        "transit_data_freshness_seconds",
        "Age of most recent transit telemetry observation in seconds",
        ["line_or_station"],
    )

# ------------------------------------------------------------------------------
# 4. NOTIFICATION & ALERTING ENGINE METRICS (Phase 8)
# ------------------------------------------------------------------------------
if "notification_events_total" in REGISTRY._names_to_collectors:
    NOTIFICATION_EVENTS_TOTAL = REGISTRY._names_to_collectors["notification_events_total"]
else:
    NOTIFICATION_EVENTS_TOTAL = Counter(
        "notification_events_total",
        "Total domain notification events recorded in Outbox",
        ["event_type", "status"],
    )

if "notification_deliveries_total" in REGISTRY._names_to_collectors:
    NOTIFICATION_DELIVERIES_TOTAL = REGISTRY._names_to_collectors["notification_deliveries_total"]
else:
    NOTIFICATION_DELIVERIES_TOTAL = Counter(
        "notification_deliveries_total",
        "Total notification delivery attempts",
        ["channel", "provider", "status"],
    )

if "notification_delivery_latency_seconds" in REGISTRY._names_to_collectors:
    NOTIFICATION_DELIVERY_LATENCY = REGISTRY._names_to_collectors["notification_delivery_latency_seconds"]
else:
    NOTIFICATION_DELIVERY_LATENCY = Histogram(
        "notification_delivery_latency_seconds",
        "Time taken by provider to process notification delivery",
        ["channel", "provider"],
        buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0],
    )

if "notification_retries_total" in REGISTRY._names_to_collectors:
    NOTIFICATION_RETRIES_TOTAL = REGISTRY._names_to_collectors["notification_retries_total"]
else:
    NOTIFICATION_RETRIES_TOTAL = Counter(
        "notification_retries_total",
        "Total notification delivery retries scheduled due to transient failures",
        ["channel", "error_code"],
    )

if "notification_suppressed_total" in REGISTRY._names_to_collectors:
    NOTIFICATION_SUPPRESSED_TOTAL = REGISTRY._names_to_collectors["notification_suppressed_total"]
else:
    NOTIFICATION_SUPPRESSED_TOTAL = Counter(
        "notification_suppressed_total",
        "Total notifications suppressed (quiet hours, user opt-out, duplicate, canceled class)",
        ["reason"],
    )

# ------------------------------------------------------------------------------
# 5. MCP (MODEL CONTEXT PROTOCOL) SERVER METRICS (Phase 7)
# ------------------------------------------------------------------------------
if "mcp_tool_calls_total" in REGISTRY._names_to_collectors:
    MCP_TOOL_CALLS_TOTAL = REGISTRY._names_to_collectors["mcp_tool_calls_total"]
else:
    MCP_TOOL_CALLS_TOTAL = Counter(
        "mcp_tool_calls_total",
        "Total MCP server tool invocations",
        ["tool_name", "status"],
    )

if "mcp_tool_duration_seconds" in REGISTRY._names_to_collectors:
    MCP_TOOL_DURATION = REGISTRY._names_to_collectors["mcp_tool_duration_seconds"]
else:
    MCP_TOOL_DURATION = Histogram(
        "mcp_tool_duration_seconds",
        "Execution duration for MCP tools in seconds",
        ["tool_name"],
        buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 3.0],
    )

if "mcp_tool_errors_total" in REGISTRY._names_to_collectors:
    MCP_TOOL_ERRORS_TOTAL = REGISTRY._names_to_collectors["mcp_tool_errors_total"]
else:
    MCP_TOOL_ERRORS_TOTAL = Counter(
        "mcp_tool_errors_total",
        "Total MCP tool execution failures categorized by error code",
        ["tool_name", "error_code"],
    )

# ------------------------------------------------------------------------------
# 6. SECURITY & THREAT METRICS
# ------------------------------------------------------------------------------
if "security_events_total" in REGISTRY._names_to_collectors:
    SECURITY_EVENTS_TOTAL = REGISTRY._names_to_collectors["security_events_total"]
else:
    SECURITY_EVENTS_TOTAL = Counter(
        "security_events_total",
        "Security-relevant events (failed logins, unauthorized cross-tenant attempts, rate limit triggers)",
        ["event_type", "severity"],
    )


# ------------------------------------------------------------------------------
# 7. SCRAPER & LEGACY TELEMETRY COLLECTORS (For backwards compatibility)
# ------------------------------------------------------------------------------
if "scraper_duration_seconds" in REGISTRY._names_to_collectors:
    SCRAPER_EXECUTION_TIME = REGISTRY._names_to_collectors["scraper_duration_seconds"]
else:
    SCRAPER_EXECUTION_TIME = Histogram(
        "scraper_duration_seconds",
        "Time spent running portal scraper",
        ["status", "target"],
        buckets=[1.0, 3.0, 5.0, 10.0, 20.0, 30.0],
    )

if "scraper_failures_total" in REGISTRY._names_to_collectors:
    SCRAPER_FAILURES_TOTAL = REGISTRY._names_to_collectors["scraper_failures_total"]
else:
    SCRAPER_FAILURES_TOTAL = Counter(
        "scraper_failures_total",
        "Total scraper failures categorized by exception",
        ["exception_type"],
    )

if "active_scraper_workers" in REGISTRY._names_to_collectors:
    ACTIVE_SCRAPER_WORKERS = REGISTRY._names_to_collectors["active_scraper_workers"]
else:
    ACTIVE_SCRAPER_WORKERS = Gauge(
        "active_scraper_workers",
        "Number of currently executing browser contexts",
    )

if "alerts_dispatched_total" in REGISTRY._names_to_collectors:
    ALERTS_DISPATCHED_TOTAL = REGISTRY._names_to_collectors["alerts_dispatched_total"]
else:
    ALERTS_DISPATCHED_TOTAL = Counter(
        "alerts_dispatched_total",
        "Total proactive notifications sent",
        ["channel", "status"],
    )


def record_cache_hit(key_prefix: str) -> None:
    CACHE_OPERATIONS_TOTAL.labels(operation=key_prefix, status="hit").inc()


def record_cache_miss(key_prefix: str) -> None:
    CACHE_OPERATIONS_TOTAL.labels(operation=key_prefix, status="miss").inc()


def record_security_event(event_type: str, severity: str = "warning") -> None:
    SECURITY_EVENTS_TOTAL.labels(event_type=event_type, severity=severity).inc()


def get_metrics_payload() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST
