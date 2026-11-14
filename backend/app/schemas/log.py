from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LogEntryResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    incident_id: UUID
    source_file: str
    line_number: int
    timestamp: datetime | None
    level: str
    message: str
    created_at: datetime


class LogUploadResponse(BaseModel):

    incident_id: UUID
    filename: str
    total_lines: int
    entries_created: int
    level_counts: dict[str, int]


class LogSummaryResponse(BaseModel):

    incident_id: UUID
    total_entries: int
    level_counts: dict[str, int]
    first_timestamp: datetime | None
    last_timestamp: datetime | None
    recent_entries: list[LogEntryResponse]


class LogFindingResponse(BaseModel):
    rule_id: str
    title: str
    severity: str
    description: str
    occurrences: int
    evidence: list[LogEntryResponse]


class LogAnalysisResponse(BaseModel):
    incident_id: UUID
    total_entries: int
    analyzed_entries: int
    findings: list[LogFindingResponse]    


class LogCorrelationGroupResponse(BaseModel):
    event_count: int
    start_timestamp: datetime
    end_timestamp: datetime
    events: list[LogEntryResponse]


class LogCorrelationResponse(BaseModel):
    incident_id: UUID
    analyzed_metrics: int
    time_window_minutes: int
    groups: list[LogCorrelationGroupResponse]
    truncated: bool
