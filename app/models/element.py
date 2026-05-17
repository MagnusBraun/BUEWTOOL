import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.enums import ElementArt


class Element(Base):
    __tablename__ = "elemente"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("objekte.id", ondelete="CASCADE"), primary_key=True
    )
    elementart: Mapped[ElementArt] = mapped_column(
        Enum(ElementArt, name="element_art", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    kabel_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("kabel.id", ondelete="SET NULL")
    )
    verteiler_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("verteiler.id", ondelete="SET NULL")
    )
    str: Mapped[int | None] = mapped_column(Integer, index=True)
    bemerkungen: Mapped[str | None] = mapped_column(Text)
    bbox_x: Mapped[float | None] = mapped_column()
    bbox_y: Mapped[float | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    objekt: Mapped["Objekt"] = relationship(back_populates="element")
    kabel: Mapped["Kabel | None"] = relationship(back_populates="elemente")
    verteiler: Mapped["Verteiler | None"] = relationship(back_populates="elemente")
