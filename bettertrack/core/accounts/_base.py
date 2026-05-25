from enum import StrEnum
from typing import TypeVar, Self

from bettertrack.core.assets import Asset
from bettertrack.core.debts import Liability


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
        """
        Get the asset account types.

        Returns
        -------
        list[AccountType]
            A list of asset account types.
        """
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
        """
        Get the liability account types.

        Returns
        -------
        list[AccountType]
            A list of liability account types.
        """
        return [
            AccountType.CREDIT_CARD,
            AccountType.MORTGAGE,
            AccountType.AUTO_LOAN,
            AccountType.STUDENT_LOAN,
            AccountType.PERSONAL_LOAN,
        ]


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
    """

    def __init__(
        self,
        institution: str,
        acc_type: AccountType,
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
