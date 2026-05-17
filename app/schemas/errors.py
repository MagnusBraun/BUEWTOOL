from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    detail: str = Field(description="Fehlerbeschreibung")
    code: str | None = Field(default=None, description="Optionaler Fehlercode")
