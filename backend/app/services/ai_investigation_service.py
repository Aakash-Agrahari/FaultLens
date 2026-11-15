from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.services.investigation_service import investigate_incident
from app.services.ai_prompt_builder import build_investigation_prompt


def serialize_log_entry(entry):
    """Convert a database log entry into plain Python data."""

    return {
        "id": str(entry.id),
        "source_file": entry.source_file,
        "line_number": entry.line_number,
        "timestamp": (
            entry.timestamp.isoformat()
            if entry.timestamp else None
        ),
        "level": entry.level,
        "message": entry.message[:2000]
    }


def prepare_ai_investigation(db: Session, incident_id: UUID):
    # Retrieve the incident.
    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    # Run the existing investigation pipeline.
    report = investigate_incident(db, incident_id)

    # Prepare incident information.
    incident_context = {
        "title": incident.title,
        "description": incident.description,
        "severity": incident.severity,
        "status": incident.status,
        "created_at": incident.created_at.isoformat()
    }

    summary = report["summary"]
    pattern_analysis = report["pattern_analysis"]
    correlations = report["correlations"]
    anomalies = report["anomalies"]

    # Prepare a compact summary.
    summary_context = {
        "total_entries": summary["total_entries"],
        "level_counts": summary["level_counts"],
        "first_timestamp": (
            summary["first_timestamp"].isoformat()
            if summary["first_timestamp"] else None
        ),
        "last_timestamp": (
            summary["last_timestamp"].isoformat()
            if summary["last_timestamp"] else None
        ),
        "recent_errors": [
            serialize_log_entry(entry)
            for entry in summary["recent_errors"]
        ]
    }

    # Prepare rule-based findings.
    pattern_context = [
        {
            "rule_id": finding["rule_id"],
            "title": finding["title"],
            "severity": finding["severity"],
            "description": finding["description"],
            "occurrences": finding["occurrences"],
            "evidence": [
                serialize_log_entry(entry)
                for entry in finding["evidence"]
            ]
        }
        for finding in pattern_analysis["findings"]
    ]

    # Prepare time-based correlations.
    correlation_context = [
        {
            "event_count": group["event_count"],
            "start_timestamp": group["start_timestamp"].isoformat(),
            "end_timestamp": group["end_timestamp"].isoformat(),
            "events": [
                serialize_log_entry(entry)
                for entry in group["events"][:5]
            ]
        }
        for group in correlations["groups"][:10]
    ]

    # Prepare anomaly findings.
    anomaly_context = [
        {
            "bucket_start": anomaly["bucket_start"].isoformat(),
            "bucket_end": anomaly["bucket_end"].isoformat(),
            "event_count": anomaly["event_count"],
            "baseline_count": anomaly["baseline_count"],
            "threshold": anomaly["threshold"],
            "evidence": [
                serialize_log_entry(entry)
                for entry in anomaly["evidence"][:5]
            ]
        }
        for anomaly in anomalies["anomalies"][:5]
    ]

    evidence_context = {
        "summary": summary_context,
        "pattern_findings": pattern_context,
        "correlation_groups": correlation_context,
        "anomalies": anomaly_context
    }

    # Generate provider-independent prompts.
    system_prompt, user_prompt = build_investigation_prompt(
        incident_context=incident_context,
        evidence_context=evidence_context
    )

    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt
    }
