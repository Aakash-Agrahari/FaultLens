from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.incident import Incident
from app.models.ai_investigation import IncidentInvestigation

from app.schemas.investigation import IncidentInvestigationResponse
from app.services.investigation_service import investigate_incident
from app.services.ai_investigation_service import run_ai_investigation

from app.schemas.ai_investigation import (
    AIInvestigationHistoryResponse,
    AIInvestigationResponse
)

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


# AI-powered investigation endpoint.
@router.post(
    "/{incident_id}/ai-investigation",
    response_model=AIInvestigationResponse
)
async def run_ai_incident_investigation(
    incident_id: UUID,
    db: Session = Depends(get_db)
):
    return await run_ai_investigation(
        db=db,
        incident_id=incident_id
    )


# Retrieve saved AI investigation history.
@router.get(
    "/{incident_id}/ai-investigations",
    response_model=AIInvestigationHistoryResponse
)
def get_ai_investigation_history(
    incident_id: UUID,
    db: Session = Depends(get_db)
):
    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    investigations = (
        db.query(IncidentInvestigation)
        .filter(
            IncidentInvestigation.incident_id == incident_id
        )
        .order_by(
            IncidentInvestigation.created_at.desc()
        )
        .all()
    )

    return {
        "incident_id": str(incident_id),
        "total": len(investigations),
        "investigations": [
            {
                "investigation_id": str(item.id),
                "status": item.status,
                "analysis": item.analysis,
                "provider": item.provider,
                "model": item.model,
                "usage": item.usage,
                "error_message": item.error_message,
                "created_at": item.created_at,
                "completed_at": item.completed_at
            }
            for item in investigations
        ]
    }