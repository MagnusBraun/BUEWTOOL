from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import (
    DocumentStatus,
    DocumentType,
    document_status_enum,
    document_type_enum,
)


class Document(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "dokumente"

    dokumenttyp: Mapped[DocumentType] = mapped_column(document_type_enum, nullable=False)
    dateiname: Mapped[str] = mapped_column(String(512), nullable=False)
    dateipfad: Mapped[str] = mapped_column(String(1024), nullable=False)
    importdatum: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    status: Mapped[DocumentStatus] = mapped_column(
        document_status_enum,
        default=DocumentStatus.HOCHGELADEN,
        nullable=False,
    )
    fehlermeldung: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Document {self.dokumenttyp.value} {self.dateiname}>"
