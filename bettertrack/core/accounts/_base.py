from enum import StrEnum
from typing import TypeVar, Self

from bettertrack.core.assets import Asset
from bettertrack.core.debts import Liability


class AccountType(StrEnum):
    BANK = "bank"
    CREDIT_UNION = "credit-union"
    BROKERAGE = "brokerage"
    CREDIT_CARD = "credit-card"


AccountHolding = TypeVar("AccountHolding", Asset, Liability)


class Account:
    """
    Base class for all accounts.

    Parameters
    ----------
    institution : str
        The institution that the account is with.
    acc_type : AccountType
        The type of account.
    acc_holdings : list[AccountHolding] | None, optional
        A list of holdings or loans associated with the account, by default None.

    Attributes
    ----------
    institution : str
        The institution that the account is with.
    account_type : AccountType
        The type of account.
    """

    def __init__(
        self,
        institution: str,
        acc_type: AccountType | str,
        acc_holdings: list[AccountHolding] | None = None,
    ):
        self._institution = institution
        self._acc_type = acc_type
        self._holdings = acc_holdings
        self._total_amt = 0.0
        self._connected_bank = None

    @property
    def institution(self) -> str:
        """
        The institution that the account is with.
        """
        return self._institution

    @property
    def account_type(self) -> AccountType:
        """
        The type of account.
        """
        return self._acc_type

    @property
    def total_amount(self) -> float:
        """
        The total amount in the account.
        """
        return self._total_amt

    def add_connected_bank(self, bank_account: Self) -> None:
        """
        Add a connected bank account to the account.

        Parameters
        ----------
        bank_account : Account
            The bank account to connect to this account.
        """
        self._connected_bank = bank_account

    def reconcile(self):
        """
        Reconcile the account.

        Raises
        ------
        NotImplementedError
            This is a base method that must be implemented by subclasses.
        """
        raise NotImplementedError()
