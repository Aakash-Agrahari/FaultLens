
import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class IncidentInvestigation(Base):
    __tablename__ = "incident_investigations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    incident_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        server_default="pending"
    )

    # Complete validated RootCauseAnalysis response.
    analysis: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )

    # Provider and model used for generation.
    provider: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    model: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    # Token usage information returned by the provider.
    usage: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
