import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Annotation(Base):
    __tablename__ = "annotationen"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    dokument_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dokumente.id", ondelete="CASCADE"), nullable=False
    )
    objekt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("objekte.id", ondelete="CASCADE"), nullable=False
    )
    x: Mapped[float] = mapped_column(nullable=False)
    y: Mapped[float] = mapped_column(nullable=False)
    breite: Mapped[float | None] = mapped_column()
    hoehe: Mapped[float | None] = mapped_column()
    text: Mapped[str | None] = mapped_column(Text)
    farbe: Mapped[str | None] = mapped_column(String(32))
    erstellt_von: Mapped[str | None] = mapped_column(String(128))
    erstellt_am: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    dokument: Mapped["Dokument"] = relationship(back_populates="annotationen")
    objekt: Mapped["Objekt"] = relationship(back_populates="annotationen")
