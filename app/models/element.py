from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import ElementType, element_type_enum

if TYPE_CHECKING:
    from app.models.cable import Cable
    from app.models.verteiler import Verteiler


class Element(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "elemente"
    __table_args__ = (UniqueConstraint("elementart", "name", name="uq_element_art_name"),)

    elementart: Mapped[ElementType] = mapped_column(element_type_enum, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    kabel_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("kabel.id", ondelete="SET NULL"),
        nullable=True,
    )
    verteiler_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("verteiler.id", ondelete="SET NULL"),
        nullable=True,
    )
    str: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bemerkungen: Mapped[str | None] = mapped_column(Text, nullable=True)

    kabel: Mapped[Cable | None] = relationship("Cable", back_populates="elemente")
    verteiler: Mapped[Verteiler | None] = relationship("Verteiler", back_populates="elemente")

    def __repr__(self) -> str:
        return f"<Element {self.elementart.value} {self.name}>"
