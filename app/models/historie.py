import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Historie(Base):
    __tablename__ = "historie"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    objekt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("objekte.id", ondelete="CASCADE"), nullable=False
    )
    feld: Mapped[str] = mapped_column(String(64), nullable=False)
    alter_wert: Mapped[str | None] = mapped_column(Text)
    neuer_wert: Mapped[str | None] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    benutzer: Mapped[str | None] = mapped_column(String(128))

    objekt: Mapped["Objekt"] = relationship(back_populates="historie_eintraege")
