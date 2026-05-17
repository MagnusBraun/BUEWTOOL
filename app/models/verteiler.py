from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import DistributorType, distributor_type_enum

if TYPE_CHECKING:
    from app.models.cable import Cable
    from app.models.element import Element


class Verteiler(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "verteiler"
    __table_args__ = (UniqueConstraint("art", "name", name="uq_verteiler_art_name"),)

    art: Mapped[DistributorType] = mapped_column(distributor_type_enum, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    km: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), nullable=True)
    str: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bemerkungen: Mapped[str | None] = mapped_column(Text, nullable=True)

    kabel_von: Mapped[list[Cable]] = relationship(
        "Cable",
        foreign_keys="Cable.von_verteiler_id",
        back_populates="von_verteiler",
    )
    kabel_bis: Mapped[list[Cable]] = relationship(
        "Cable",
        foreign_keys="Cable.bis_verteiler_id",
        back_populates="bis_verteiler",
    )
    elemente: Mapped[list[Element]] = relationship(
        "Element",
        back_populates="verteiler",
    )

    def __repr__(self) -> str:
        return f"<Verteiler {self.art.value} {self.name}>"
