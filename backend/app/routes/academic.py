from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from ..core.config import settings
from ..core.rate_limiter import limiter
from ..scrapers.base_adapter import CampusAdapterRegistry
from ..scrapers.exceptions import PortalAuthError
from ..services.academic_orchestrator import AcademicOrchestrator

router = APIRouter(prefix="/api/v1/academic", tags=["Academic"])

class CredentialsPayload(BaseModel):
    username: str
    password: str
    campus_code: str = "MU_STANDARD"

# In a real application, the orchestrator would be injected via a dependency
# For this implementation, we define a provider function
async def get_orchestrator():
    # This is a simplified injection. In production, these would be managed by the app state.
    # We'll assume they are available on the app state or managed globally.
    from ..main import app
    return app.state.orchestrator

@router.post("/attendance/{student_id}")
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_attendance(
    request: Request,
    student_id: str,
    payload: CredentialsPayload,
    orchestrator: AcademicOrchestrator = Depends(get_orchestrator)
):
    try:
        CampusAdapterRegistry.get_adapter(payload.campus_code)
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))

    try:
        return await orchestrator.get_attendance(student_id, payload.model_dump())
    except PortalAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.post("/exams/{student_id}")
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_exams(
    request: Request,
    student_id: str,
    payload: CredentialsPayload,
    orchestrator: AcademicOrchestrator = Depends(get_orchestrator)
):
    try:
        return await orchestrator.get_exams(student_id, payload.dict())
    except PortalAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
