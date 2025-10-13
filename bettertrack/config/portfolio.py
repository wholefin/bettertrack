from datetime import datetime

from pydantic import BaseModel

from bettertrack.core.accounts import Account, AccountType, AssetAccount, DebtAccount
from bettertrack.core.debts import Liability, LiabilityType
from bettertrack.core.assets import Asset, AssetType


class AssetConfig(BaseModel):
    """
    Configuration for an asset.

    Parameters
    ----------
    type_ : str
        The type of asset.
    name : str
        The name of the asset.
    ticker : str
        The ticker symbol of the asset.
    shares : float, optional
        The number of shares owned, by default 0.0.
    cost_basis : float | None, optional
        The cost basis of the asset, by default None.
    yield_ : float | None, optional
        The yield of the asset, by default None.
    expense_ratio : float, optional
        The expense ratio of the asset, by default 0.0.
    """

    type_: AssetType
    name: str
    ticker: str
    shares: float = 0.0
    cost_basis: float | None = None
    yield_: float | None = None
    expense_ratio: float = 0.0

    def to_asset(self) -> Asset:
        """
        Convert the AssetConfig to an Asset instance.

        Returns
        -------
        Asset
            An instance of the Asset class.
        """
        return Asset(
            type_=self.type_,
            name=self.name,
            ticker=self.ticker,
            shares=self.shares,
            cost_basis=self.cost_basis,
            yield_=self.yield_,
            expense_ratio=self.expense_ratio,
        )


class DebtConfig(BaseModel):
    """
    Configuration for a debt.

    Parameters
    ----------
    type_ : str
        The type of debt.
    name : str
        The name of the debt.
    apr : float
        The annual percentage rate of the debt.
    og_principal : float
        The original principal amount of the debt.
    tenure : int
        The tenure of the debt in months.
    """

    type_: LiabilityType
    name: str
    apr: float
    og_principal: float
    tenure: int

    def to_liability(self) -> Liability:
        """
        Convert the DebtConfig to a Loan instance.

        Returns
        -------
        Liability
            An instance of the Loan class.
        """
        return Liability(
            type_=self.type_,
            name=self.name,
            apr=self.apr,
            og_principal=self.og_principal,
            tenure=self.tenure,
        )


class AccountConfig(BaseModel):
    """
    Configuration for an account.

    Parameters
    ----------
    institution : str
        The institution that the account is with.
    acc_type : str
        The type of account.
    acc_holdings : list[AssetConfig | DebtConfig] | None, optional
        A list of holdings or loans associated with the account, by default None.
    cash : float, optional
        Amount of cash in the account, by default 0.0.
    """

    institution: str
    acc_type: AccountType
    acc_holdings: list[AssetConfig | DebtConfig] | None = None
    cash: float = 0.0

    def to_account(self) -> Account:
        """
        Convert the AccountConfig to an Account instance.

        Returns
        -------
        Account
            An instance of the Account (AssetAccount or DebtAccount) class.
        """
        # Determine if this is an asset or debt account based on holdings
        has_debts = self.acc_holdings and any(
            isinstance(h, DebtConfig) for h in self.acc_holdings
        )
        has_assets = self.acc_holdings and any(
            isinstance(h, AssetConfig) for h in self.acc_holdings
        )

        if has_debts:
            # Create DebtAccount
            debt_holdings = [
                h.to_liability() for h in self.acc_holdings if isinstance(h, DebtConfig)
            ]
            return DebtAccount(
                institution=self.institution,
                acc_type=self.acc_type,
                acc_holdings=debt_holdings,
            )
        else:
            # Create AssetAccount (default)
            acc = AssetAccount(
                institution=self.institution,
                acc_type=self.acc_type,
            )

            # Add cash if present
            if self.cash > 0:
                acc.transfer_in(self.cash)

            # Add asset holdings directly to preserve cost basis
            if has_assets:
                for holding_cfg in self.acc_holdings:
                    if isinstance(holding_cfg, AssetConfig):
                        asset = holding_cfg.to_asset()
                        acc._holdings[asset.ticker] = asset

            return acc


class PortfolioConfig(BaseModel):
    """
    Configuration for a portfolio.

    Parameters
    ----------
    name : str
        The name of the portfolio.
    owner : str
        The owner of the portfolio.
    accounts : list[AccountConfig]
        A list of accounts associated with the portfolio.
    last_updated : datetime | None, optional
        The last time the portfolio was updated, by default None.
    created_at : datetime, optional
        The time the portfolio was created, by default datetime.now().
    """

    name: str
    owner: str
    accounts: list[AccountConfig]
    last_updated: datetime | None = None
    created_at: datetime = datetime.now()
