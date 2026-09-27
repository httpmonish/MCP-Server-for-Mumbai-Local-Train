from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .logger import get_logger, get_request_context
from .telemetry import record_security_event

logger = get_logger("core.errors")


def create_error_payload(
    code: str,
    message: str,
    request_id: Optional[str] = None,
    details: Optional[Any] = None,
) -> Dict[str, Any]:
    ctx = get_request_context()
    req_id = request_id or ctx.get("request_id") or "req_unknown"
    payload: Dict[str, Any] = {
        "detail": details if details is not None else message,
        "error": {
            "code": code,
            "message": message,
            "request_id": req_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }
    if details is not None and isinstance(details, (dict, list)):
        payload["error"]["details"] = details
    return payload


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    ctx = get_request_context()
    req_id = ctx.get("request_id") or "req_unknown"

    code = "HTTP_ERROR"
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        code = "AUTHENTICATION_REQUIRED"
        record_security_event(event_type="auth_unauthorized", severity="warning")
    elif exc.status_code == status.HTTP_403_FORBIDDEN:
        code = "PERMISSION_DENIED"
        record_security_event(event_type="permission_denied", severity="warning")
    elif exc.status_code == status.HTTP_404_NOT_FOUND:
        code = "RESOURCE_NOT_FOUND"
    elif exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
        code = "VALIDATION_ERROR"
    elif exc.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
        code = "SERVICE_UNAVAILABLE"

    # Detail could be string or dict
    msg = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    details = exc.detail if isinstance(exc.detail, dict) else None

    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_payload(code=code, message=msg, request_id=req_id, details=details),
        headers={"X-Request-ID": req_id},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    ctx = get_request_context()
    req_id = ctx.get("request_id") or "req_unknown"
    safe_errors = jsonable_encoder(exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_payload(
            code="SCHEMA_VALIDATION_FAILED",
            message="Request body or parameters failed validation schema.",
            request_id=req_id,
            details=safe_errors,
        ),
        headers={"X-Request-ID": req_id},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    ctx = get_request_context()
    req_id = ctx.get("request_id") or "req_unknown"

    logger.error(
        f"Unhandled system exception: {exc.__class__.__name__}: {str(exc)}",
        exc_info=True,
        extra={"path": request.url.path, "method": request.method, "request_id": req_id},
    )

    # Never leak raw SQL, traceback, or internal system secrets to clients
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_payload(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred. Please contact support with the request ID.",
            request_id=req_id,
        ),
        headers={"X-Request-ID": req_id},
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
