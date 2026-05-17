from uuid import UUID

from pydantic import BaseModel


class VlpImportResponse(BaseModel):
    dokument_id: UUID
    status: str
    stats: dict
    unmatched_names: list[str]
    warnings: list[str]
