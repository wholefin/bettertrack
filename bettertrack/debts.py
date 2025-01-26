from dataclasses import dataclass
from enum import StrEnum


class DebtType(StrEnum):
    AUTO = "auto-loan"
    HOUSE = "house-loan"
    EDUCATION = "student-loan"
    CREDIT_CARD = "credit-card-debt"
    PERSONAL = "personal-loan"


@dataclass(slots=True)
class Loan:
    type_: DebtType
    name: str
    apr: float
    og_principal: float
    tenure: int

