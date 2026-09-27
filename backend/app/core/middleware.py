import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings
from .logger import clear_request_context, get_logger, set_request_context
from .telemetry import HTTP_REQUEST_DURATION, HTTP_REQUESTS_TOTAL

logger = get_logger("core.middleware")


class ObservabilityAndSecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware that:
    1. Propagates or generates correlation IDs (X-Request-ID and X-Trace-ID).
    2. Populates structured logging contextvars.
    3. Measures request latency and records Prometheus HTTP metrics.
    4. Attaches production-grade security headers to all outgoing responses.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract or generate Request ID & Trace ID
        incoming_req_id = request.headers.get("X-Request-ID") or request.headers.get("X-Correlation-ID")
        request_id = incoming_req_id if incoming_req_id and len(incoming_req_id) <= 64 else f"req_{uuid.uuid4().hex[:16]}"
        trace_id = f"trc_{uuid.uuid4().hex}"

        set_request_context(request_id=request_id, trace_id=trace_id)

        start_time = time.perf_counter()
        status_code = 500
        path_template = request.url.path

        try:
            response: Response = await call_next(request)
            status_code = response.status_code
        except Exception as exc:
            duration_s = time.perf_counter() - start_time
            duration_ms = round(duration_s * 1000, 2)
            HTTP_REQUESTS_TOTAL.labels(
                method=request.method,
                route=path_template,
                status_code=str(500),
            ).inc()
            HTTP_REQUEST_DURATION.labels(
                method=request.method,
                route=path_template,
                status_code=str(500),
            ).observe(duration_s)
            logger.error(
                f"Unhandled exception during HTTP request: {exc}",
                extra={
                    "method": request.method,
                    "path": path_template,
                    "status_code": 500,
                    "duration_ms": duration_ms,
                    "error_type": exc.__class__.__name__,
                },
            )
            clear_request_context()
            raise exc

        duration_s = time.perf_counter() - start_time
        duration_ms = round(duration_s * 1000, 2)

        # Record Prometheus Metrics (low cardinality route grouping)
        # Normalize route for metrics (strip IDs to prevent explosion if possible, or use path)
        metric_route = path_template
        if "/trains/" in metric_route:
            metric_route = "/api/v1/trains/*"
        elif "/organizations/" in metric_route:
            metric_route = "/api/v1/organizations/*"
        elif "/schedules/" in metric_route:
            metric_route = "/api/v1/schedules/*"

        HTTP_REQUESTS_TOTAL.labels(
            method=request.method,
            route=metric_route,
            status_code=str(status_code),
        ).inc()
        HTTP_REQUEST_DURATION.labels(
            method=request.method,
            route=metric_route,
            status_code=str(status_code),
        ).observe(duration_s)

        # Add Correlation Headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Trace-ID"] = trace_id

        # Attach Security Headers
        if getattr(settings, "SECURITY_HEADERS_ENABLED", True):
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # Structured Log for Request Completion
        log_level = logger.info if status_code < 400 else (logger.warning if status_code < 500 else logger.error)
        log_level(
            f"HTTP {request.method} {path_template} -> {status_code} ({duration_ms}ms)",
            extra={
                "method": request.method,
                "path": path_template,
                "status_code": status_code,
                "duration_ms": duration_ms,
            },
        )

        clear_request_context()
        return response
