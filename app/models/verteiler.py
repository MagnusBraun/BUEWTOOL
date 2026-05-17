import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.enums import VerteilerArt


class Verteiler(Base):
    __tablename__ = "verteiler"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("objekte.id", ondelete="CASCADE"), primary_key=True
    )
    art: Mapped[VerteilerArt] = mapped_column(
        Enum(VerteilerArt, name="verteiler_art", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    km: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    str: Mapped[int | None] = mapped_column(Integer)
    bemerkungen: Mapped[str | None] = mapped_column(Text)
    bbox_x: Mapped[float | None] = mapped_column()
    bbox_y: Mapped[float | None] = mapped_column()
    bbox_breite: Mapped[float | None] = mapped_column()
    bbox_hoehe: Mapped[float | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    objekt: Mapped["Objekt"] = relationship(back_populates="verteiler")
    kabel_von: Mapped[list["Kabel"]] = relationship(
        back_populates="von_ort", foreign_keys="Kabel.von_ort_id"
    )
    kabel_bis: Mapped[list["Kabel"]] = relationship(
        back_populates="bis_ort", foreign_keys="Kabel.bis_ort_id"
    )
    elemente: Mapped[list["Element"]] = relationship(back_populates="verteiler")
