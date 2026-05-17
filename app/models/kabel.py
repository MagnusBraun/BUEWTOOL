import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Kabel(Base):
    __tablename__ = "kabel"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("objekte.id", ondelete="CASCADE"), primary_key=True
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    typ: Mapped[str | None] = mapped_column(String(64))
    index: Mapped[str | None] = mapped_column(String(16))
    durchmesser: Mapped[str | None] = mapped_column(String(32))
    trommelnummer: Mapped[str | None] = mapped_column(String(64))
    von_ort_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("verteiler.id", ondelete="SET NULL")
    )
    bis_ort_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("verteiler.id", ondelete="SET NULL")
    )
    von_km: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    von_metrierung: Mapped[str | None] = mapped_column(String(64))
    bis_km: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    bis_metrierung: Mapped[str | None] = mapped_column(String(64))
    laenge_soll: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    laenge_ist: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    verlegeart: Mapped[str | None] = mapped_column(String(64))
    vlp_nummer: Mapped[str | None] = mapped_column(String(64))
    bemerkungen: Mapped[str | None] = mapped_column(Text)
    str: Mapped[int | None] = mapped_column(Integer, index=True)
    streckenuebergreifend: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    geom_line: Mapped[list | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    objekt: Mapped["Objekt"] = relationship(back_populates="kabel")
    von_ort: Mapped["Verteiler | None"] = relationship(
        back_populates="kabel_von", foreign_keys=[von_ort_id]
    )
    bis_ort: Mapped["Verteiler | None"] = relationship(
        back_populates="kabel_bis", foreign_keys=[bis_ort_id]
    )
    elemente: Mapped[list["Element"]] = relationship(back_populates="kabel")
