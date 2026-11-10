
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.schemas.incident import (IncidentCreate,IncidentUpdate)


def create_incident(
    db: Session,
    incident_data: IncidentCreate
):
    incident = Incident(
        title=incident_data.title,
        description=incident_data.description,
        severity=incident_data.severity
    )

    db.add(incident)
    db.commit()
    db.refresh(incident)

    return incident


def get_all_incidents(db: Session):
    statement = select(Incident).order_by(
        Incident.created_at.desc()
    )

    return db.scalars(statement).all()


def get_incident_by_id(
    db: Session,
    incident_id: UUID
):
    return db.get(Incident, incident_id)


def update_incident(
    db: Session,
    incident: Incident,
    incident_data: IncidentUpdate
):
    update_data = incident_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        if value is not None:
            setattr(incident, field, value)

    if update_data:
        db.commit()
        db.refresh(incident)

    return incident


def delete_incident(
    db: Session,
    incident: Incident
):
    db.delete(incident)
    db.commit()
