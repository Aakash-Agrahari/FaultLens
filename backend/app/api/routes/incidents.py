from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.schemas.incident import (IncidentCreate,IncidentResponse)

from app.services.incident_service import (create_incident,get_all_incidents)

router = APIRouter(
    prefix="/api/v1/incidents",
    tags=["Incidents"]
)


@router.post(
    "/",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_new_incident(incident_data: IncidentCreate, db: Session = Depends(get_db)):
    return create_incident(db, incident_data)


@router.get("/", response_model=list[IncidentResponse])
def list_incidents(db: Session = Depends(get_db)):
    return get_all_incidents(db)
