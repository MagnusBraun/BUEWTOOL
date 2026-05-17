from uuid import UUID

from pydantic import BaseModel


class KuepParseResponse(BaseModel):
    dokument_id: UUID
    status: str
    stats: dict[str, int]
    warnings: list[str]
    pages_processed: int
