from uuid import UUID

from pydantic import BaseModel, Field


class ValidationRequest(BaseModel):
    projekt_id: UUID


class ValidationSummary(BaseModel):
    gelb: int
    rot: int
    gesamt: int


class ValidationIssue(BaseModel):
    severity: str
    regel: str
    message: str
    objekt_id: str | None = None
    objekt_typ: str | None = None
    feld: str | None = None
    referenz: str | None = None


class ValidationResponse(BaseModel):
    projekt_id: UUID
    summary: ValidationSummary
    issues: list[ValidationIssue]
