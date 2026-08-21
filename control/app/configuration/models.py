from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from control.app.network.models import Base


class ControlConfiguration(Base):
    __tablename__ = "control_configuration"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    effective_json: Mapped[str] = mapped_column(Text, nullable=False)
    proposed_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    previous_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
