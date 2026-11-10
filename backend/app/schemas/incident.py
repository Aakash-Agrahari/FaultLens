from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


IncidentSeverity = Literal[
    "low",
    "medium",
    "high",
    "critical"
]

IncidentStatus = Literal[
    "open",
    "investigating",
    "resolved",
    "closed"
]


class IncidentCreate(BaseModel):
    title: str = Field(min_length=5, max_length=150)

    description: str = Field(min_length=10, max_length=2000)

    severity: IncidentSeverity = "medium"


class IncidentUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=5,
        max_length=150
    )

    description: str | None = Field(
        default=None,
        min_length=10,
        max_length=2000
    )

    severity: IncidentSeverity | None = None

    status: IncidentStatus | None = None


class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str
    severity: str
    status: str
    created_at: datetime
