from datetime import datetime
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, Field

class IncidentCreate(BaseModel):
    title: str = Field(
        min_length=5,
        max_length=150
    )

    description: str = Field(
        min_length = 10,
        max_length = 2000
    )

    severity: Literal[
        "low",
        "medium",
        "high",
        "critical",
    ] = "medium"


class IncidentResponse(BaseModel):
    id: UUID
    title: str
    description: str
    severity: str
    status: str
    created_at: datetime    