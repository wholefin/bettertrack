from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field

from bettertrack.core.accounts import Account


class Portfolio(BaseModel):
    """A user's full portfolio: a named collection of Accounts."""

    name: str
    owner: str
    accounts: list[Account] | None = None
    last_updated: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)

    def save(self, path: Path) -> None:
        path.write_text(self.model_dump_json(indent=4))
