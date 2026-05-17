from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDPrimaryKeyMixin
from app.models.enums import ObjectType, object_type_enum


class Annotation(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "annotationen"

    dokument_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("dokumente.id", ondelete="CASCADE"),
        nullable=False,
    )
    objekt_typ: Mapped[ObjectType] = mapped_column(object_type_enum, nullable=False)
    objekt_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    seite: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    x: Mapped[float] = mapped_column(Float, nullable=False)
    y: Mapped[float] = mapped_column(Float, nullable=False)
    breite: Mapped[float] = mapped_column(Float, nullable=False)
    hoehe: Mapped[float] = mapped_column(Float, nullable=False)
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    farbe: Mapped[str | None] = mapped_column(String(32), nullable=True)
    erstellt_von: Mapped[str | None] = mapped_column(String(255), nullable=True)
    erstellt_am: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
