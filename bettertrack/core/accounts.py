from enum import StrEnum
from typing import Self

from pydantic import BaseModel, Field

from bettertrack.core.assets import Asset
from bettertrack.core.debts import Liability
from bettertrack.exceptions import OutOfCashError
from bettertrack.price import get_current_price


class AccountType(StrEnum):
    BANK = "bank"
    BROKERAGE = "brokerage"
    RETIREMENT = "retirement"
    HSA = "hsa"
    CRYPTO_WALLET = "crypto-wallet"
    CASH = "cash"
    REAL_ESTATE = "real-estate"

    CREDIT_CARD = "credit-card"
    MORTGAGE = "mortgage"
    AUTO_LOAN = "auto-loan"
    STUDENT_LOAN = "student-loan"
    PERSONAL_LOAN = "personal-loan"

    @staticmethod
    def get_asset_types() -> list["AccountType"]:
        return [
            AccountType.BANK,
            AccountType.BROKERAGE,
            AccountType.RETIREMENT,
            AccountType.HSA,
            AccountType.CRYPTO_WALLET,
            AccountType.CASH,
            AccountType.REAL_ESTATE,
        ]

    @staticmethod
    def get_liability_types() -> list["AccountType"]:
        return [
            AccountType.CREDIT_CARD,
            AccountType.MORTGAGE,
            AccountType.AUTO_LOAN,
            AccountType.STUDENT_LOAN,
            AccountType.PERSONAL_LOAN,
        ]


class Account(BaseModel):
    """
    A single account in a portfolio.

    `is_asset` discriminates asset accounts (cash + Asset holdings) from
    liability accounts (Liability holdings). Methods that only make sense
    for one kind raise RuntimeError when called on the wrong kind.
    """

    account_id: int
    institution: str
    acc_type: AccountType
    acc_holdings: list[Asset | Liability] | None = None
    cash: float = 0.0
    is_asset: bool = True
    # Runtime-only state (not persisted to JSON).
    total_amount: float = Field(default=0.0, exclude=True)
    connected_bank: "Account | None" = Field(default=None, exclude=True)

    # ------------------------------------------------------------------
    # Shared
    # ------------------------------------------------------------------
    def add_connected_bank(self, bank_account: Self) -> None:
        self.connected_bank = bank_account

    def reconcile(self) -> float:
        """Recompute and store this account's total value."""
        holdings = self.acc_holdings or []
        if self.is_asset:
            self.total_amount = self.cash + sum(
                h.shares * get_current_price(h.ticker) for h in holdings
            )
        else:
            self.total_amount = sum(h.og_principal for h in holdings)
        return self.total_amount

    # ------------------------------------------------------------------
    # Asset-only
    # ------------------------------------------------------------------
    def _require_asset(self, op: str) -> None:
        if not self.is_asset:
            raise RuntimeError(f"{op} is only valid on asset accounts")

    def transfer_in(self, amt: float, _: Self | None = None) -> float:
        self._require_asset("transfer_in")
        self.cash += amt
        return self.cash

    def transfer_out(self, amt: float, _: Self | None = None) -> float:
        self._require_asset("transfer_out")
        if amt > self.cash:
            raise OutOfCashError("Not enough cash in account!")
        self.cash -= amt
        return self.cash

    def buy(self, amt: float, holding: Asset) -> float:
        self._require_asset("buy")
        if amt > self.cash:
            raise OutOfCashError("Not enough cash in account!")

        holding.cost_basis = get_current_price(holding.ticker)
        holding.shares = amt / holding.cost_basis

        if self.acc_holdings is None:
            self.acc_holdings = []

        # Combine with an existing holding of the same ticker, if any.
        for idx, existing in enumerate(self.acc_holdings):
            if isinstance(existing, Asset) and existing.ticker == holding.ticker:
                self.acc_holdings[idx] = existing + holding
                break
        else:
            self.acc_holdings.append(holding)

        self.cash -= amt
        return self.cash

    def sell(self) -> float:
        self._require_asset("sell")
        raise NotImplementedError()

    def dividend(self) -> float:
        self._require_asset("dividend")
        raise NotImplementedError()

    def interest(self) -> float:
        self._require_asset("interest")
        raise NotImplementedError()

    # ------------------------------------------------------------------
    # Liability-only
    # ------------------------------------------------------------------
    def make_payment(self, amt: float, src_account: Self | None = None) -> float:
        if self.is_asset:
            raise RuntimeError("make_payment is only valid on liability accounts")
        raise NotImplementedError()
