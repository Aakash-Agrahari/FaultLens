
from collections import Counter
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.models.log_entry import LogEntry
from app.services.log_parser import parse_log_file


def process_log_upload(
    db: Session,
    incident_id: UUID,
    filename: str,
    content: str
):
    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    parsed_entries = parse_log_file(content)

    if not parsed_entries:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file contains no log entries"
        )

    log_entries = [
        LogEntry(
            incident_id=incident_id,
            source_file=filename,
            **entry
        )
        for entry in parsed_entries
    ]

    try:
        db.add_all(log_entries)
        db.commit()

        for entry in log_entries:
            db.refresh(entry)

    except Exception:
        db.rollback()
        raise

    level_counts = dict(
        Counter(entry["level"] for entry in parsed_entries)
    )

    return {
        "incident_id": incident_id,
        "filename": filename,
        "total_lines": len(content.splitlines()),
        "entries_created": len(log_entries),
        "level_counts": level_counts
    }


def get_incident_logs(
    db: Session,
    incident_id: UUID
):
    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    statement = (
        select(LogEntry)
        .where(LogEntry.incident_id == incident_id)
        .order_by(LogEntry.line_number.asc())
    )

    return db.scalars(statement).all()
