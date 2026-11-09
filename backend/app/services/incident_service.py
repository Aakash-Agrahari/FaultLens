from datetime import datetime, timezone
from uuid import uuid4

from app.schemas.incident import (IncidentCreate, IncidentResponse)

incidents = []

def create_incident(incident_data: IncidentCreate) -> IncidentResponse:
    incident = IncidentResponse(
        id=uuid4(),
        title=incident_data.title,
        description=incident_data.description,
        severity=incident_data.severity,
        status="open",
        created_at=datetime.now(timezone.utc)
    )
    incidents.append(incident)
    return incident

def get_all_incidents() -> list[IncidentResponse]:
    return incidents