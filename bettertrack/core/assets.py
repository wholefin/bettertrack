from enum import StrEnum
from typing import Self

from pydantic import BaseModel


class AssetType(StrEnum):
    STOCKS = "stocks"
    BONDS = "bonds"
    MONEY_MARKET = "money-market"
    HYBRID = "hybrid"
    CD = "cd"
    CASH = "cash"
    REAL_ESTATE = "real-estate"
    CRYPTO = "crypto-currency"
    COMMODITY = "commodity"


class Asset(BaseModel):
    """A single holding inside an asset account."""

    type_: AssetType
    name: str
    ticker: str
    shares: float = 0.0
    cost_basis: float | None = None
    yield_: float | None = None
    expense_ratio: float = 0.0

    def dividend(self) -> float:
        raise NotImplementedError()

    def interest(self) -> float:
        raise NotImplementedError()

    def __add__(self, other: Self) -> Self:
        """Combine two holdings of the same ticker, weighted by cost basis."""
        if self.ticker != other.ticker:
            raise TypeError("Cannot operate on different holdings!")

        if not self.shares:
            return other

        total_shares = self.shares + other.shares
        new_cost_basis = (
            self.shares * self.cost_basis + other.shares * other.cost_basis
        ) / total_shares
        return self.model_copy(
            update={"shares": total_shares, "cost_basis": new_cost_basis}
        )

    def __eq__(self, other: object) -> bool:
        # Ticker-only equality: two holdings of VOO are "the same" for combining.
        if not isinstance(other, Asset):
            return NotImplemented
        return self.ticker == other.ticker

    __hash__ = None  # type: ignore[assignment]
