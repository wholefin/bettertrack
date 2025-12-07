from typing import Self

from bettertrack.core.debts import Liability
from bettertrack.core.accounts._base import Account, AccountType


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
