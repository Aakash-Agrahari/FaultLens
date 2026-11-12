from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

class LogEntryRespone(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    incident_id: UUID
    source_files: str
    line_number:int
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