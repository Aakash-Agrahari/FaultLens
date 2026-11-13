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