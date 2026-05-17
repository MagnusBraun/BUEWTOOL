import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.enums import DokumentStatus, DokumentTyp


class Dokument(Base):
    __tablename__ = "dokumente"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    projekt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projekte.id", ondelete="CASCADE"), nullable=False
    )
    dokumenttyp: Mapped[DokumentTyp] = mapped_column(
        Enum(DokumentTyp, name="dokument_typ", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    dateiname: Mapped[str] = mapped_column(String(512), nullable=False)
    dateipfad: Mapped[str] = mapped_column(Text, nullable=False)
    importdatum: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    status: Mapped[DokumentStatus] = mapped_column(
        Enum(DokumentStatus, name="dokument_status", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=DokumentStatus.IMPORTIERT,
    )
    metadaten: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    projekt: Mapped["Projekt"] = relationship(back_populates="dokumente")
    annotationen: Mapped[list["Annotation"]] = relationship(back_populates="dokument")
    vlp_zeilen: Mapped[list["VlpImportZeile"]] = relationship(back_populates="dokument")
