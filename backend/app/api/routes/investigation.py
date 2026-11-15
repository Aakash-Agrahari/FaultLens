from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.investigation import IncidentInvestigationResponse
from app.services.investigation_service import investigate_incident

router = APIRouter(
    prefix="/api/v1/incidents",
    tags=["Incident Investigation"]
)

@router.get(
    "/{incident_id}/investigation",
    response_model=IncidentInvestigationResponse
)
def run_incident_investigation(
    incident_id: UUID,
    db: Session = Depends(get_db)
):
    return investigate_incident(db, incident_id)