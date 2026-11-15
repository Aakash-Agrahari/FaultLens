from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.log import(
    LogSummaryResponse,
    LogAnalysisResponse,
    LogCorrelationResponse,
    LogAnomalyResponse
)

class IncidentInvestigationResponse(BaseModel):
    incident_id: UUID
    generated_at: datetime
    summary: LogSummaryResponse
    pattern_analysis: LogAnalysisResponse
    correlations: LogCorrelationResponse
    anomalies: LogAnomalyResponse