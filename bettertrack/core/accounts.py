from enum import StrEnum
from typing import Self, TypeVar

from bettertrack.core.assets import Asset
from bettertrack.core.debts import Liability
from bettertrack.exceptions import OutOfCashError
from bettertrack.price import get_current_price


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


class AssetAccount(Account):
    """
    A class for asset based accounts.

    Parameters
    ----------
    institution : str
        The institution that the account is with.
    acc_type : AccountType
        The type of account.
    acc_holdings : list[Holding] | None, optional
        A list of holdings associated with the account, by default None.

    Attributes
    ----------
    cash : float
        The amount of cash in the account.
    holdings : list[Asset]
        The holdings in the account.
    """

    def __init__(
        self,
        institution: str,
        acc_type: AccountType,
        acc_holdings: list[Asset] | None = None,
    ):
        super().__init__(institution, acc_type, acc_holdings=acc_holdings)
        self._holdings: dict[str, Asset] = {}
        self._cash_amt = 0.0

    @property
    def cash(self) -> float:
        """
        The amount of cash in the account.
        """
        return self._cash_amt

    @property
    def holdings(self) -> list[Asset]:
        """
        The holdings in the account.
        """
        return list(self._holdings.values())

    def transfer_in(self, amt: float, _: Self | None = None) -> float:
        """
        Transfer cash into the account.

        Parameters
        ----------
        amt : float
            The amount to transfer in
        _ : Self | None, optional
            Unused parameter for transfer source, by default None

        Returns
        -------
        float
            The new cash balance after transfer
        """
        self._cash_amt += amt
        return self._cash_amt

    def transfer_out(self, amt: float, _: Self | None = None) -> float:
        self._cash_amt -= amt
        return self._cash_amt

    def buy(self, amt: float, holding: Asset) -> float:
        """
        Buy a holding with the specified amount.

        Parameters
        ----------
        amt : float
            The amount to spend on the purchase.
        holding : Asset
            The holding to buy.

        Returns
        -------
        float
            The remaining cash balance after the purchase.

        Raises
        ------
        OutOfCashError
            If there is not enough cash in the account for the purchase.
        """
        if amt > self._cash_amt:
            raise OutOfCashError("Not enough cash in account!")

        holding.cost_basis = get_current_price(holding.ticker)
        holding.shares = amt / holding.cost_basis

        try:
            self._holdings[holding.ticker] += holding
        except KeyError:
            self._holdings[holding.ticker] = holding

        self._cash_amt -= amt
        return self._cash_amt

    def sell(self) -> float:
        """
        Sell holdings from the account.

        Returns
        -------
        float
            The proceeds from the sale.
        """
        pass

    def dividend(self) -> float:
        """
        Process dividend payments for holdings.

        Returns
        -------
        float
            The total dividend amount.
        """
        pass

    def interest(self) -> float:
        """
        Calculate interest earned on the account.

        Returns
        -------
        float
            The interest amount earned.
        """
        pass

    def reconcile(self) -> float:
        """
        Reconcile the account and calculate total value.
        This calculates the total value as cash + market value of all holdings.

        Returns
        -------
        float
            The total value of the account.
        """
        # Start with cash
        total = self._cash_amt

        # Add market value of each holding
        for holding in self._holdings.values():
            current_price = get_current_price(holding.ticker)
            market_value = holding.shares * current_price
            total += market_value

        # Update the _total_amt
        self._total_amt = total
        return self._total_amt


class DebtAccount(Account):
    """
    A class for debt-based accounts.

    Parameters
    ----------
    institution : str
        The institution that the account is with.
    acc_type : AccountType
        The type of account.
    acc_holdings : list[Loan] | None, optional
        A list of loans associated with the account, by default None.

    Attributes
    ----------
    outstanding_balance : float
        The remaining balance on the loan.
    remaining_months : int
        The number of months remaining on the loan term.

    Raises
    ------
    NotImplementedError
        If multiple loan entries are provided (currently not supported).
    """

    def __init__(
        self,
        institution: str,
        acc_type: AccountType,
        acc_holdings: list[Liability] | None = None,
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
        """
        Make a payment on the debt account.

        Parameters
        ----------
        amt : float
            The payment amount.
        src_account : Account | None, optional
            The source account for the payment, by default None.

        Returns
        -------
        float
            The remaining balance after the payment.
        """
        pass

    def reconcile(self) -> float:
        """
        Reconcile the debt account and calculate total outstanding balance.

        Returns
        -------
        float
            The total outstanding debt balance.
        """
        total = 0.0
        if self._holdings:
            for liability in self._holdings:
                total += liability.og_principal

        self._total_amt = total
        return self._total_amt
