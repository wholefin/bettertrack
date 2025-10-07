from copy import copy
from enum import StrEnum
from dataclasses import dataclass
from typing import Self


class AssetType(StrEnum):
    STOCKS = "stocks"
    BONDS = "bonds"
    MONEY_MARKET = "money-market"
    CD = "cd"
    CASH = "cash"
    REAL_ESTATE = "real-estate"
    CRYPTO = "crypto-currency"
    COMMODITY = "commodity"


@dataclass(slots=True)
class Asset:
    type_: AssetType
    name: str
    ticker: str
    shares: float = 0.0
    cost_basis: float | None = None
    yield_: float | None = None
    expense_ratio: float = 0.0

    def dividend(self):
        pass

    def interest(self):
        pass

    def __add__(self, other: Self) -> Self:
        if self.ticker != other.ticker:
            raise TypeError("Cannot operate on different holdings!")

        if not self.shares:
            return other

        holding = copy(self)
        total_shares = holding.shares + other.shares
        new_cost_basis = (
            holding.shares * holding.cost_basis + other.shares * other.cost_basis
        ) / total_shares

        holding.shares = total_shares
        holding.cost_basis = new_cost_basis
        return holding

    def __eq__(self, other):
        return self.ticker == other.ticker
