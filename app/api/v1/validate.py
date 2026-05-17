from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.validation import (
    ValidationIssue,
    ValidationRequest,
    ValidationResponse,
    ValidationSummary,
)
from app.services.validation_service import ValidationService

router = APIRouter(tags=["validation"])


@router.post("/validate", response_model=ValidationResponse)
def validate_projekt(
    body: ValidationRequest,
    db: Session = Depends(get_db),
) -> ValidationResponse:
    result = ValidationService(db, body.projekt_id).validate()
    return ValidationResponse(
        projekt_id=body.projekt_id,
        summary=ValidationSummary(**result["summary"]),
        issues=[ValidationIssue(**i) for i in result["issues"]],
    )
