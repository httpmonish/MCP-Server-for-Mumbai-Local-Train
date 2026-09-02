from fastapi import APIRouter
from fastapi.responses import Response

from ..core.telemetry import get_metrics_payload

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("", include_in_schema=False)
@router.get("/", include_in_schema=False)
async def metrics_endpoint():
    body, content_type = get_metrics_payload()
    return Response(content=body, media_type=content_type)
