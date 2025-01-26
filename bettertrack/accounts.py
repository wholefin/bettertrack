from enum import StrEnum
from typing import Self, TypeVar

from bettertrack.assets import Holding
from bettertrack.debts import Loan
from bettertrack.exceptions import OutOfCashError
from bettertrack.price import get_asset_price


class AccountType(StrEnum):
    BANK = "bank"
    CREDIT_UNION = "credit-union"
    BROKERAGE = "brokerage"
    CREDIT_CARD = "credit-card"


AccountHolding = TypeVar("AccountHolding", Holding, Loan)


class Account:
    def __init__(
        self,
        institution: str,
        acc_type: AccountType,
        acc_holdings: list[AccountHolding] | None = None,
    ):
        self._institution = institution
        self._acc_type = acc_type
        self._holdings = acc_holdings
        self._total_amt = None
        self._connected_bank = None

    @property
    def institution(self) -> str:
        return self._institution

    @property
    def account_type(self) -> AccountType:
        return self._acc_type

    def add_connected_bank(self, bank_account: Self) -> None:
        self._connected_bank = bank_account

    def reconcile(self):
        raise NotImplementedError()


class AssetAccount(Account):
    def __init__(
        self,
        institution: str,
        acc_type: AccountType,
        acc_holdings: list[Holding] | None = None,
    ):
        super().__init__(institution, acc_type, acc_holdings=acc_holdings)
        self._holdings: dict[str, Holding] = {}
        self._cash_amt = 0.0

    @property
    def cash(self) -> float:
        return self._cash_amt

    @property
    def holdings(self) -> list[Holding]:
        return list(self._holdings.values())

    def transfer_in(self, amt: float, _: Self | None = None) -> float:
        self._cash_amt += amt
        return self._cash_amt

    def transfer_out(self, amt: float, _: Self | None = None) -> float:
        self._cash_amt -= amt
        return self._cash_amt

    def buy(self, amt: float, holding: Holding) -> float:
        if amt > self._cash_amt:
            raise OutOfCashError("Not enough cash in account!")

        holding.cost_basis = get_asset_price(holding.ticker)
        holding.shares = amt / holding.cost_basis

        try:
            self._holdings[holding.ticker] += holding
        except KeyError:
            self._holdings[holding.ticker] = holding

        self._cash_amt -= amt
        return self._cash_amt

    def sell(self) -> float:
        pass

    def dividend(self) -> float:
        pass

    def interest(self) -> float:
        pass


class DebtAccount(Account):
    def __init__(
        self,
        institution: str,
        acc_type: AccountType,
        acc_holdings: list[Loan] | None = None,
    ):
        if acc_holdings and len(acc_holdings) > 1:
            err_msg = "Multiple loan entries for a debt account not yet supported"
            raise NotImplementedError(err_msg)
        super().__init__(institution, acc_type, acc_holdings=acc_holdings)
        self._amt_remaining = None
        self._months_remaining = None

    @property
    def outstanding_balance(self) -> float:
        return self._amt_remaining

    @property
    def remaining_months(self) -> int:
        return self._months_remaining

    def make_payment(self, amt: float, src_account: Self | None = None) -> float:
        pass
