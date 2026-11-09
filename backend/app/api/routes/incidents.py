from fastapi import APIRouter, status
from app.schemas.incident import (IncidentCreate, IncidentResponse)
from app.services.incident_service import (create_incident, get_all_incidents)

router = APIRouter(
    prefix="/api/v1/incidents",
    tags=["Incidents"]
)

@router.post(
    "/",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_new_incident(incident_data: IncidentCreate):
    return create_incident(incident_data)

@router.get("/", response_model=list[IncidentResponse])
def list_incidents():
    return get_all_incidents()
