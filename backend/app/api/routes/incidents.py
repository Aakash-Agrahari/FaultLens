
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status
)

from sqlalchemy.orm import Session

from app.db.database import get_db

from app.schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResponse
)

from app.services.incident_service import (
    create_incident,
    get_all_incidents,
    get_incident_by_id,
    update_incident,
    delete_incident
)


router = APIRouter(
    prefix="/api/v1/incidents",
    tags=["Incidents"]
)


@router.post(
    "/",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_new_incident(
    incident_data: IncidentCreate,
    db: Session = Depends(get_db)
):
    return create_incident(db, incident_data)


@router.get(
    "/",
    response_model=list[IncidentResponse]
)
def list_incidents(
    db: Session = Depends(get_db)
):
    return get_all_incidents(db)


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse
)
def retrieve_incident(
    incident_id: UUID,
    db: Session = Depends(get_db)
):
    incident = get_incident_by_id(
        db,
        incident_id
    )

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    return incident


@router.patch(
    "/{incident_id}",
    response_model=IncidentResponse
)
def modify_incident(
    incident_id: UUID,
    incident_data: IncidentUpdate,
    db: Session = Depends(get_db)
):
    incident = get_incident_by_id(
        db,
        incident_id
    )

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    return update_incident(
        db,
        incident,
        incident_data
    )


@router.delete(
    "/{incident_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_incident(
    incident_id: UUID,
    db: Session = Depends(get_db)
):
    incident = get_incident_by_id(
        db,
        incident_id
    )

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    delete_incident(db, incident)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
