from dataclasses import dataclass
from enum import StrEnum


class LiabilityType(StrEnum):
    AUTO = "auto-loan"
    HOUSE = "house-loan"
    EDUCATION = "student-loan"
    CREDIT_CARD = "credit-card-debt"
    PERSONAL = "personal-loan"


@dataclass(slots=True)
class Liability:
    type_: LiabilityType
    name: str
    apr: float
    og_principal: float
    tenure: int
