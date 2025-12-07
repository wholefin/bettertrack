from typing import Self

from bettertrack.core.assets import Asset
from bettertrack.core.accounts._base import Account, AccountType
from bettertrack.exceptions import OutOfCashError
from bettertrack.price import get_current_price


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
