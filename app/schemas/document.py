from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import DocumentStatus, DocumentType


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    dokumenttyp: DocumentType
    dateiname: str
    dateipfad: str
    importdatum: datetime
    status: DocumentStatus
    fehlermeldung: str | None = None
    created_at: datetime
    updated_at: datetime


class UploadResponse(BaseModel):
    message: str = Field(description="Statusmeldung des Uploads")
    document: DocumentResponse
