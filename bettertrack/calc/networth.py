from bettertrack.config.portfolio import PortfolioConfig
from bettertrack.core.accounts import AssetAccount, DebtAccount


def compute_networth(portfolio_conf: PortfolioConfig) -> float:
    calculator = NetworthCalculator(portfolio_conf)
    return calculator.calculate_networth()


class NetworthCalculator:
    def __init__(self, portfolio_conf: PortfolioConfig):
        self._accounts = [acc.to_account() for acc in portfolio_conf.accounts]
        self._networth = 0.0

    @property
    def networth(self) -> float:
        return self._networth

    def calculate_networth(self) -> float:
        self._networth = 0.0
        for account in self._accounts:
            # Reconcile account to update total_amount
            account.reconcile()

            if isinstance(account, AssetAccount):
                self._networth += account.total_amount
            elif isinstance(account, DebtAccount):
                self._networth -= account.total_amount
        return self._networth
