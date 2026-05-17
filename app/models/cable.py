from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.element import Element
    from app.models.verteiler import Verteiler


class Cable(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "kabel"
    __table_args__ = (UniqueConstraint("name", name="uq_kabel_name"),)

    name: Mapped[str] = mapped_column(String(64), nullable=False)
    typ: Mapped[str | None] = mapped_column(String(128), nullable=True)
    index: Mapped[str | None] = mapped_column(String(32), nullable=True)
    durchmesser: Mapped[str | None] = mapped_column(String(64), nullable=True)
    trommelnummer: Mapped[str | None] = mapped_column(String(64), nullable=True)

    von_verteiler_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("verteiler.id", ondelete="SET NULL"),
        nullable=True,
    )
    bis_verteiler_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("verteiler.id", ondelete="SET NULL"),
        nullable=True,
    )

    von_ort: Mapped[str | None] = mapped_column(String(255), nullable=True)
    von_km: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), nullable=True)
    von_metrierung: Mapped[str | None] = mapped_column(String(64), nullable=True)
    bis_ort: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bis_km: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), nullable=True)
    bis_metrierung: Mapped[str | None] = mapped_column(String(64), nullable=True)

    laenge_soll: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    laenge_ist: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    verlegeart: Mapped[str | None] = mapped_column(String(128), nullable=True)
    vlp_nummer: Mapped[str | None] = mapped_column(String(64), nullable=True)
    bemerkungen: Mapped[str | None] = mapped_column(Text, nullable=True)

    str: Mapped[int | None] = mapped_column(Integer, nullable=True)
    streckenuebergreifend: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    von_verteiler: Mapped[Verteiler | None] = relationship(
        "Verteiler",
        foreign_keys=[von_verteiler_id],
        back_populates="kabel_von",
    )
    bis_verteiler: Mapped[Verteiler | None] = relationship(
        "Verteiler",
        foreign_keys=[bis_verteiler_id],
        back_populates="kabel_bis",
    )
    elemente: Mapped[list[Element]] = relationship(
        "Element",
        back_populates="kabel",
    )

    def __repr__(self) -> str:
        return f"<Cable {self.name}>"
