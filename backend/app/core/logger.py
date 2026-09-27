import contextvars
import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# Context variables for tracing & correlation
_request_id_ctx = contextvars.ContextVar[Optional[str]]("request_id", default=None)
_trace_id_ctx = contextvars.ContextVar[Optional[str]]("trace_id", default=None)
_user_id_ctx = contextvars.ContextVar[Optional[str]]("user_id", default=None)
_org_id_ctx = contextvars.ContextVar[Optional[str]]("org_id", default=None)


def set_request_context(
    request_id: Optional[str] = None,
    trace_id: Optional[str] = None,
    user_id: Optional[str] = None,
    org_id: Optional[str] = None,
) -> None:
    if request_id is not None:
        _request_id_ctx.set(request_id)
    if trace_id is not None:
        _trace_id_ctx.set(trace_id)
    if user_id is not None:
        _user_id_ctx.set(user_id)
    if org_id is not None:
        _org_id_ctx.set(org_id)


def get_request_context() -> Dict[str, Optional[str]]:
    return {
        "request_id": _request_id_ctx.get(),
        "trace_id": _trace_id_ctx.get(),
        "user_id": _user_id_ctx.get(),
        "org_id": _org_id_ctx.get(),
    }


def clear_request_context() -> None:
    _request_id_ctx.set(None)
    _trace_id_ctx.set(None)
    _user_id_ctx.set(None)
    _org_id_ctx.set(None)


# Sensitive keyword pattern matcher for log redaction
SENSITIVE_PATTERNS = [
    re.compile(r"(password[\"'\s:=]+)([\"']?[^\"'\s,]+[\"']?)", re.IGNORECASE),
    re.compile(r"(token[\"'\s:=]+)([\"']?[^\"'\s,]+[\"']?)", re.IGNORECASE),
    re.compile(r"(secret[\"'\s:=]+)([\"']?[^\"'\s,]+[\"']?)", re.IGNORECASE),
    re.compile(r"(api[_-]?key[\"'\s:=]+)([\"']?[^\"'\s,]+[\"']?)", re.IGNORECASE),
    re.compile(r"(authorization[\"'\s:=]+Bearer\s+)([^\s\"',]+)", re.IGNORECASE),
    re.compile(r"(Bearer\s+)([A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+\.?[A-Za-z0-9\-_.+/=]*)", re.IGNORECASE),
]


def redact_sensitive_text(text: str) -> str:
    if not isinstance(text, str):
        return text
    redacted = text
    for pattern in SENSITIVE_PATTERNS:
        redacted = pattern.sub(r"\1[REDACTED]", redacted)
    return redacted


def redact_dict(data: Any) -> Any:
    if isinstance(data, dict):
        cleaned = {}
        for k, v in data.items():
            if any(s in k.lower() for s in ["password", "secret", "token", "key", "auth", "credential", "jwt"]):
                cleaned[k] = "[REDACTED]"
            else:
                cleaned[k] = redact_dict(v)
        return cleaned
    elif isinstance(data, list):
        return [redact_dict(item) for item in data]
    elif isinstance(data, str):
        return redact_sensitive_text(data)
    return data


class StructuredJSONFormatter(logging.Formatter):
    """
    Outputs logs in production-ready structured JSON format with correlation
    metadata and automated sensitive field redaction.
    """

    def __init__(self, service_name: str = "transitpulse-backend", environment: str = "production"):
        super().__init__()
        self.service_name = service_name
        self.environment = environment

    def format(self, record: logging.LogRecord) -> str:
        ctx = get_request_context()
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": redact_sensitive_text(record.getMessage()),
            "service": self.service_name,
            "environment": self.environment,
            "request_id": ctx.get("request_id"),
            "trace_id": ctx.get("trace_id"),
            "user_id": ctx.get("user_id"),
            "org_id": ctx.get("org_id"),
        }

        # Include custom extra attributes if passed
        for key, val in record.__dict__.items():
            if key not in [
                "args", "asctime", "created", "exc_info", "exc_text", "filename",
                "funcName", "levelname", "levelno", "lineno", "module", "msecs",
                "message", "msg", "name", "pathname", "process", "processName",
                "relativeCreated", "stack_info", "thread", "threadName"
            ]:
                log_entry[key] = redact_dict(val)

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


class SecretRedactionFilter(logging.Filter):
    """Filter ensuring any message passing through standard logging has sensitive info redacted."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = redact_sensitive_text(record.msg)
        return True


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        from .config import settings

        if getattr(settings, "LOG_FORMAT", "json").lower() == "console":
            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
            )
        else:
            formatter = StructuredJSONFormatter(
                service_name=settings.PROJECT_NAME,
                environment=settings.ENVIRONMENT,
            )

        handler.setFormatter(formatter)
        handler.addFilter(SecretRedactionFilter())
        logger.addHandler(handler)

        log_level_name = getattr(settings, "LOG_LEVEL", "INFO").upper()
        log_level = getattr(logging, log_level_name, logging.INFO)
        logger.setLevel(log_level)
        logger.propagate = False

    return logger
