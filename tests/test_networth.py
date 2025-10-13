import json
from pathlib import Path
import pytest

from bettertrack.config.portfolio import PortfolioConfig
from bettertrack.calc.networth import compute_networth, NetworthCalculator
from bettertrack.core.accounts import AssetAccount, DebtAccount


@pytest.fixture
def comprehensive_portfolio_path():
    """Path to comprehensive portfolio JSON with assets and debts"""
    return Path(__file__).parent / "fixtures" / "sample_portfolio.json"


@pytest.fixture
def comprehensive_portfolio_data(comprehensive_portfolio_path):
    """Load comprehensive portfolio JSON data"""
    with open(comprehensive_portfolio_path) as f:
        return json.load(f)


def test_compute_networth_with_comprehensive_portfolio(comprehensive_portfolio_data):
    """Test calculating net worth from a comprehensive portfolio with assets and debts"""
    # Arrange
    portfolio = PortfolioConfig(**comprehensive_portfolio_data)

    # Act
    networth = compute_networth(portfolio)

    # Assert
    assert isinstance(networth, float)
    # Sample portfolio has significant mortgage debt, so net worth is negative
    assert networth < 0

    print(f"\n{'='*80}")
    print("NET WORTH CALCULATION TEST")
    print(f"{'='*80}")
    print(f"Calculated Net Worth: ${networth:,.2f}")


def test_networth_calculator_breakdown(comprehensive_portfolio_data):
    """Test detailed breakdown of net worth calculation"""
    # Arrange
    portfolio = PortfolioConfig(**comprehensive_portfolio_data)
    calculator = NetworthCalculator(portfolio)

    # Act
    networth = calculator.calculate_networth()

    # Assert
    assert networth == calculator.networth

    # Detailed breakdown - use the same accounts from the calculator
    total_assets = 0.0
    total_debts = 0.0

    print(f"\n{'='*80}")
    print("DETAILED NET WORTH BREAKDOWN")
    print(f"{'='*80}\n")

    for account in calculator._accounts:
        print(f"Institution: {account.institution}")
        print(f"Type: {account.account_type}")

        if isinstance(account, AssetAccount):
            print(f"  Cash: ${account.cash:,.2f}")

            if account.holdings:
                print("  Holdings:")
                for holding in account.holdings:
                    from bettertrack.price import get_current_price

                    # Use cached price to match what reconcile calculated
                    current_price = get_current_price(holding.ticker)
                    market_value = holding.shares * current_price
                    print(
                        f"    - {holding.ticker}: {holding.shares:.2f} shares @ ${current_price:.2f} = ${market_value:,.2f}"
                    )

            print(f"  Total: ${account.total_amount:,.2f}")
            total_assets += account.total_amount

        elif isinstance(account, DebtAccount):
            if account._holdings:
                print("  Debts:")
                for liability in account._holdings:
                    print(
                        f"    - {liability.name}: ${liability.og_principal:,.2f} @ {liability.apr}% APR"
                    )

            print(f"  Total Debt: ${account.total_amount:,.2f}")
            total_debts += account.total_amount

        print(f"{'-'*80}\n")

    print(f"{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Total Assets:  ${total_assets:>15,.2f}")
    print(f"Total Debts:   ${total_debts:>15,.2f}")
    print(f"{'-'*80}")
    print(f"NET WORTH:     ${networth:>15,.2f}")
    print(f"{'='*80}\n")

    # Assertions
    assert total_assets > 0
    assert total_debts > 0
    assert (
        abs(networth - (total_assets - total_debts)) < 0.01
    )  # Allow for floating point precision


def test_asset_account_reconcile():
    """Test that AssetAccount.reconcile() calculates correct total"""
    # Arrange
    from bettertrack.config.portfolio import AssetConfig, AccountConfig
    from bettertrack.core.assets import AssetType
    from bettertrack.core.accounts import AccountType
    from unittest.mock import patch

    asset_config = AssetConfig(
        type_=AssetType.STOCKS,
        name="Test Stock",
        ticker="TEST",
        shares=100.0,
        cost_basis=50.0,
    )

    account_config = AccountConfig(
        institution="Test Brokerage",
        acc_type=AccountType.BROKERAGE,
        cash=10000.0,
        acc_holdings=[asset_config],
    )

    # Act
    account = account_config.to_account()

    # Mock the price function to return a known value
    with patch("bettertrack.core.accounts.get_current_price", return_value=75.0):
        total = account.reconcile()

    # Assert
    assert isinstance(account, AssetAccount)
    assert account.cash == 10000.0
    assert len(account.holdings) == 1
    # 100 shares @ $75 + $10,000 cash = $17,500
    assert total == 17500.0
    assert account.total_amount == total


def test_debt_account_reconcile():
    """Test that DebtAccount.reconcile() calculates correct total"""
    # Arrange
    from bettertrack.config.portfolio import DebtConfig, AccountConfig
    from bettertrack.core.debts import LiabilityType
    from bettertrack.core.accounts import AccountType

    debt_config = DebtConfig(
        type_=LiabilityType.AUTO,
        name="Car Loan",
        apr=4.5,
        og_principal=25000.0,
        tenure=60,
    )

    account_config = AccountConfig(
        institution="Bank",
        acc_type=AccountType.CREDIT_CARD,
        cash=0.0,
        acc_holdings=[debt_config],
    )

    # Act
    account = account_config.to_account()
    total = account.reconcile()

    # Assert
    assert isinstance(account, DebtAccount)
    assert total == 25000.0
    assert account.total_amount == 25000.0


def test_networth_calculator_with_only_assets():
    """Test net worth calculation with only asset accounts"""
    # Arrange

    portfolio_data = {
        "name": "Assets Only Portfolio",
        "owner": "Test User",
        "accounts": [
            {
                "institution": "Bank",
                "acc_type": "bank",
                "cash": 50000.0,
                "acc_holdings": None,
            },
        ],
    }

    portfolio = PortfolioConfig(**portfolio_data)

    # Act
    networth = compute_networth(portfolio)

    # Assert
    assert networth == 50000.0


def test_networth_calculator_with_only_debts():
    """Test net worth calculation with only debt accounts"""
    # Arrange
    portfolio_data = {
        "name": "Debts Only Portfolio",
        "owner": "Test User",
        "accounts": [
            {
                "institution": "Lender",
                "acc_type": "credit-card",
                "cash": 0.0,
                "acc_holdings": [
                    {
                        "type_": "student-loan",
                        "name": "Student Loan",
                        "apr": 5.0,
                        "og_principal": 30000.0,
                        "tenure": 120,
                    }
                ],
            },
        ],
    }

    portfolio = PortfolioConfig(**portfolio_data)

    # Act
    networth = compute_networth(portfolio)

    # Assert
    assert networth == -30000.0  # Negative net worth
