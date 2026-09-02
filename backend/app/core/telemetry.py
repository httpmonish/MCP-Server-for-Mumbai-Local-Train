from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

if "scraper_duration_seconds" in REGISTRY._names_to_collectors:
    SCRAPER_EXECUTION_TIME = REGISTRY._names_to_collectors["scraper_duration_seconds"]
else:
    SCRAPER_EXECUTION_TIME = Histogram(
        "scraper_duration_seconds",
        "Time spent running Playwright portal scraper",
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

if "cache_operations_total" in REGISTRY._names_to_collectors:
    CACHE_OPERATIONS_TOTAL = REGISTRY._names_to_collectors["cache_operations_total"]
else:
    CACHE_OPERATIONS_TOTAL = Counter(
        "cache_operations_total",
        "Redis cache lookups",
        ["operation", "status"],
    )

if "active_scraper_workers" in REGISTRY._names_to_collectors:
    ACTIVE_SCRAPER_WORKERS = REGISTRY._names_to_collectors["active_scraper_workers"]
else:
    ACTIVE_SCRAPER_WORKERS = Gauge(
        "active_scraper_workers",
        "Number of currently executing Playwright browser contexts",
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


def get_metrics_payload() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST
