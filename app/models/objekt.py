import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.enums import ObjektTyp


class Objekt(Base):
    __tablename__ = "objekte"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    projekt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projekte.id", ondelete="CASCADE"), nullable=False
    )
    objekt_typ: Mapped[ObjektTyp] = mapped_column(
        Enum(ObjektTyp, name="objekt_typ", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    projekt: Mapped["Projekt"] = relationship(back_populates="objekte")
    verteiler: Mapped["Verteiler | None"] = relationship(
        back_populates="objekt", uselist=False, cascade="all, delete-orphan"
    )
    kabel: Mapped["Kabel | None"] = relationship(
        back_populates="objekt", uselist=False, cascade="all, delete-orphan"
    )
    element: Mapped["Element | None"] = relationship(
        back_populates="objekt", uselist=False, cascade="all, delete-orphan"
    )
    historie_eintraege: Mapped[list["Historie"]] = relationship(back_populates="objekt")
    annotationen: Mapped[list["Annotation"]] = relationship(back_populates="objekt")
