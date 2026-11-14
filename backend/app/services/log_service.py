
from collections import Counter
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, func
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



def get_log_summary(db: Session, incident_id: UUID):
    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    # Count log entries by severity directly in PostgreSQL.
    count_statement = (
        select(LogEntry.level, func.count(LogEntry.id))
        .where(LogEntry.incident_id == incident_id)
        .group_by(LogEntry.level)
    )

    level_counts = {
        level: count
        for level, count in db.execute(count_statement).all()
    }

    total_entries = sum(level_counts.values())

    # Find the earliest and latest log timestamps.
    timestamp_statement = select(
        func.min(LogEntry.timestamp),
        func.max(LogEntry.timestamp)
    ).where(LogEntry.incident_id == incident_id)

    first_timestamp, last_timestamp = db.execute(
        timestamp_statement
    ).one()

    # Retrieve the five most recent errors or critical events.
    error_statement = (
        select(LogEntry)
        .where(
            LogEntry.incident_id == incident_id,
            LogEntry.level.in_(["ERROR", "CRITICAL"])
        )
        .order_by(
            LogEntry.timestamp.desc().nullslast(),
            LogEntry.line_number.desc()
        )
        .limit(5)
    )

    recent_errors = db.scalars(error_statement).all()

    return {
        "incident_id": incident_id,
        "total_entries": total_entries,
        "level_counts": level_counts,
        "first_timestamp": first_timestamp,
        "last_timestamp": last_timestamp,
        "recent_errors": recent_errors
    }



def get_log_analysis(db: Session, incident_id: UUID):
    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    # Count all entries belonging to this incident.
    total_entries = db.scalar(
        select(func.count())
        .select_from(LogEntry)
        .where(LogEntry.incident_id == incident_id)
    ) or 0

    # Analyze warning and higher-severity entries.
    statement = (
        select(LogEntry)
        .where(
            LogEntry.incident_id == incident_id,
            LogEntry.level.in_(["WARNING", "ERROR", "CRITICAL"])
        )
        .order_by(LogEntry.line_number.asc())
    )

    entries = db.scalars(statement).all()

    # Each rule describes a potential problem.
    rules = [
        {
            "rule_id": "DATABASE_CONNECTION_FAILURE",
            "title": "Database connection failures",
            "severity": "critical",
            "description": "The logs indicate repeated database connection failures.",
            "keywords": [
                "connection refused",
                "database connection failed",
                "could not connect to database",
                "database unavailable"
            ]
        },
        {
            "rule_id": "TIMEOUT_DETECTED",
            "title": "Timeout detected",
            "severity": "high",
            "description": "One or more operations appear to be exceeding their allowed response time.",
            "keywords": [
                "timeout",
                "timed out",
                "time out"
            ]
        },
        {
            "rule_id": "MEMORY_PRESSURE",
            "title": "Memory-related problem",
            "severity": "high",
            "description": "The logs indicate possible memory exhaustion or high memory usage.",
            "keywords": [
                "out of memory",
                "memory usage",
                "heap space",
                "oom"
            ]
        },
        {
            "rule_id": "SERVICE_UNAVAILABLE",
            "title": "Service unavailable",
            "severity": "critical",
            "description": "A service may be unavailable or failing to handle requests.",
            "keywords": [
                "service unavailable",
                "503 service",
                "payment service unavailable"
            ]
        },
        {
            "rule_id": "AUTHENTICATION_FAILURE",
            "title": "Authentication failure",
            "severity": "medium",
            "description": "The logs indicate possible authentication or authorization failures.",
            "keywords": [
                "unauthorized",
                "authentication failed",
                "token expired",
                "invalid token"
            ]
        }
    ]

    findings = []

    for rule in rules:
        matched_entries = []

        for entry in entries:
            message = entry.message.lower()

            if any(keyword in message for keyword in rule["keywords"]):
                matched_entries.append(entry)

        if matched_entries:
            findings.append({
                "rule_id": rule["rule_id"],
                "title": rule["title"],
                "severity": rule["severity"],
                "description": rule["description"],
                "occurrences": len(matched_entries),
                "evidence": matched_entries[:3]
            })

    return {
        "incident_id": incident_id,
        "total_entries": total_entries,
        "analyzed_entries": len(entries),
        "findings": findings
    }
