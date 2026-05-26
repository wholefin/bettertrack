from enum import StrEnum

from pydantic import BaseModel


class LiabilityType(StrEnum):
    AUTO = "auto-loan"
    HOUSE = "house-loan"
    EDUCATION = "student-loan"
    CREDIT_CARD = "credit-card-debt"
    PERSONAL = "personal-loan"


class Liability(BaseModel):
    """A single liability inside a debt account."""

    type_: LiabilityType
    name: str
    apr: float
    og_principal: float
    tenure: int
