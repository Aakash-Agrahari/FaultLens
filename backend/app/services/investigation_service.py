from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.incident import Incident

from app.services.log_service import (
    get_log_summary,
    get_log_analysis,
    get_log_correlations,
    get_log_anomalies
)

def investigate_incident(db: Session, incident_id: UUID):
    incident = db.get(Incident, incident_id) #confirm that the incident exists
    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    #collect the results from our existing investigation
    summary = get_log_summary(db, incident_id)
    pattern_analysis = get_log_analysis(db, incident_id)
    correlations = get_log_correlations(db, incident_id)
    anomalies = get_log_anomalies(db, incident_id)

    #combine everything into one investigation report
    return(
        "incident_id": incident_id,
        "generated_at": datetime.now(timezone.utc),
        "summary": summary,
        "pattern_analysis": pattern_analysis,
        "correlations": correlations,
        "anomalies": anomalies
    )