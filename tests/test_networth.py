import json
from pathlib import Path
from unittest.mock import patch

import pytest

from bettertrack.calc.networth import NetworthCalculator, compute_networth
from bettertrack.core.accounts import Account, AccountType
from bettertrack.core.assets import Asset, AssetType
from bettertrack.core.debts import Liability, LiabilityType
from bettertrack.core.portfolio import Portfolio


@pytest.fixture
def comprehensive_portfolio_data():
    path = Path(__file__).parent / "fixtures" / "sample_portfolio.json"
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Per-account reconcile()
# ---------------------------------------------------------------------------


def test_asset_account_reconcile_uses_market_price():
    account = Account(
        account_id=1,
        institution="Test Brokerage",
        acc_type=AccountType.BROKERAGE,
        is_asset=True,
        cash=10000.0,
        acc_holdings=[
            Asset(
                type_=AssetType.STOCKS,
                name="Test",
                ticker="TEST",
                shares=100.0,
                cost_basis=50.0,
            )
        ],
    )

    with patch("bettertrack.core.accounts.get_current_price", return_value=75.0):
        total = account.reconcile()

    # 100 shares @ $75 + $10,000 cash = $17,500
    assert total == 17500.0
    assert account.total_amount == 17500.0


def test_asset_account_reconcile_cash_only():
    account = Account(
        account_id=1,
        institution="Bank",
        acc_type=AccountType.BANK,
        is_asset=True,
        cash=50000.0,
    )
    assert account.reconcile() == 50000.0


def test_debt_account_reconcile_sums_principal():
    account = Account(
        account_id=1,
        institution="Bank",
        acc_type=AccountType.AUTO_LOAN,
        is_asset=False,
        cash=0.0,
        acc_holdings=[
            Liability(
                type_=LiabilityType.AUTO,
                name="Car Loan",
                apr=4.5,
                og_principal=25000.0,
                tenure=60,
            )
        ],
    )
    assert account.reconcile() == 25000.0
    assert account.total_amount == 25000.0


# ---------------------------------------------------------------------------
# NetworthCalculator
# ---------------------------------------------------------------------------


def test_networth_only_assets():
    portfolio = Portfolio(
        name="Assets Only",
        owner="me",
        accounts=[
            Account(
                account_id=1,
                institution="Bank",
                acc_type=AccountType.BANK,
                is_asset=True,
                cash=50000.0,
            )
        ],
    )
    assert compute_networth(portfolio) == 50000.0


def test_networth_only_debts():
    portfolio = Portfolio(
        name="Debts Only",
        owner="me",
        accounts=[
            Account(
                account_id=1,
                institution="Lender",
                acc_type=AccountType.STUDENT_LOAN,
                is_asset=False,
                cash=0.0,
                acc_holdings=[
                    Liability(
                        type_=LiabilityType.EDUCATION,
                        name="Student Loan",
                        apr=5.0,
                        og_principal=30000.0,
                        tenure=120,
                    )
                ],
            )
        ],
    )
    assert compute_networth(portfolio) == -30000.0


def test_compute_networth_with_comprehensive_portfolio(comprehensive_portfolio_data):
    """Mixed portfolio: significant mortgage debt should yield negative net worth."""
    portfolio = Portfolio(**comprehensive_portfolio_data)
    with patch("bettertrack.core.accounts.get_current_price", return_value=100.0):
        networth = compute_networth(portfolio)

    assert isinstance(networth, float)
    # Sample fixture has ~$320k mortgage + ~$25k auto — assets won't outweigh.
    assert networth < 0


def test_networth_calculator_breakdown(comprehensive_portfolio_data):
    """Sum of asset totals minus sum of liability totals equals overall networth."""
    portfolio = Portfolio(**comprehensive_portfolio_data)
    calculator = NetworthCalculator(portfolio)

    with patch("bettertrack.core.accounts.get_current_price", return_value=100.0):
        networth = calculator.calculate_networth()

    total_assets = 0.0
    total_debts = 0.0
    for account in calculator._accounts:
        if account.is_asset:
            total_assets += account.total_amount
        else:
            total_debts += account.total_amount

    assert total_assets > 0
    assert total_debts > 0
    assert abs(networth - (total_assets - total_debts)) < 0.01
    assert networth == calculator.networth
