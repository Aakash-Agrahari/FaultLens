from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.schemas.investigation import IncidentInvestigationResponse

from app.services.investigation_service import investigate_incident
from app.services.ai_investigation_service import run_ai_investigation


router = APIRouter(
    prefix="/api/v1/incidents",
    tags=["Incident Investigation"]
)


# Existing rule-based investigation endpoint.
@router.get(
    "/{incident_id}/investigation",
    response_model=IncidentInvestigationResponse
)
def run_incident_investigation(
    incident_id: UUID,
    db: Session = Depends(get_db)
):
    return investigate_incident(db, incident_id)


# New AI-powered investigation endpoint.
@router.post(
    "/{incident_id}/ai-investigation"
)
async def run_ai_incident_investigation(
    incident_id: UUID,
    db: Session = Depends(get_db)
):
    return await run_ai_investigation(
        db=db,
        incident_id=incident_id
    )
