from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDPrimaryKeyMixin
from app.models.enums import ObjectType, object_type_enum


class History(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "historie"

    objekt_typ: Mapped[ObjectType] = mapped_column(object_type_enum, nullable=False)
    objekt_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    feld: Mapped[str] = mapped_column(String(128), nullable=False)
    alter_wert: Mapped[str | None] = mapped_column(Text, nullable=True)
    neuer_wert: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    benutzer: Mapped[str] = mapped_column(String(255), default="system", nullable=False)
