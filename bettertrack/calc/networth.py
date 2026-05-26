from bettertrack.core.portfolio import Portfolio


def compute_networth(portfolio: Portfolio) -> float:
    return NetworthCalculator(portfolio).calculate_networth()


class NetworthCalculator:
    def __init__(self, portfolio: Portfolio):
        self._accounts = list(portfolio.accounts or [])
        self._networth = 0.0

    @property
    def networth(self) -> float:
        return self._networth

    def calculate_networth(self) -> float:
        self._networth = 0.0
        for account in self._accounts:
            account.reconcile()
            if account.is_asset:
                self._networth += account.total_amount
            else:
                self._networth -= account.total_amount
        return self._networth
