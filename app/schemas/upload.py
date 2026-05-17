from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.db.enums import DokumentStatus, DokumentTyp


class UploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    dokument_id: UUID
    projekt_id: UUID
    dateiname: str
    dokumenttyp: DokumentTyp
    status: DokumentStatus
    message: str
