import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class VlpImportZeile(Base):
    __tablename__ = "vlp_import_zeilen"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    dokument_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dokumente.id", ondelete="CASCADE"), nullable=False
    )
    kabel_name: Mapped[str | None] = mapped_column(String(64))
    laenge_ist: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    trommelnummer: Mapped[str | None] = mapped_column(String(64))
    verlegeart: Mapped[str | None] = mapped_column(String(64))
    vlp_nummer: Mapped[str | None] = mapped_column(String(64))
    rohdaten: Mapped[dict | None] = mapped_column(JSONB)
    matched_kabel_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("kabel.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    dokument: Mapped["Dokument"] = relationship(back_populates="vlp_zeilen")
