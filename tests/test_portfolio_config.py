import json
from pathlib import Path
import pytest
from datetime import datetime

from bettertrack.config.portfolio import (
    AssetConfig,
    AccountConfig,
    DebtConfig,
    PortfolioConfig,
)
from bettertrack.core.assets import Asset, AssetType
from bettertrack.core.debts import Loan, DebtType
from bettertrack.core.accounts import Account, AccountType


@pytest.fixture
def sample_portfolio_path():
    """Path to sample portfolio JSON fixture"""
    return Path(__file__).parent / "fixtures" / "sample_portfolio.json"


@pytest.fixture
def sample_portfolio_data(sample_portfolio_path):
    """Load sample portfolio JSON data"""
    with open(sample_portfolio_path) as f:
        return json.load(f)


def test_asset_config_to_asset():
    """Test converting AssetConfig to Asset dataclass"""
    # Arrange
    asset_config = AssetConfig(
        type_=AssetType.STOCKS,
        name="Vanguard Total Stock Market ETF",
        ticker="VTI",
        shares=100.5,
        cost_basis=200.0,
        yield_=1.5,
        expense_ratio=0.03,
    )

    # Act
    asset = asset_config.to_asset()

    # Assert
    assert isinstance(asset, Asset)
    assert asset.type_ == AssetType.STOCKS
    assert asset.ticker == "VTI"
    assert asset.shares == 100.5
    assert asset.cost_basis == 200.0
    assert asset.yield_ == 1.5
    assert asset.expense_ratio == 0.03


def test_debt_config_to_loan():
    """Test converting DebtConfig to Loan dataclass"""
    # Arrange
    debt_config = DebtConfig(
        type_=DebtType.HOUSE,
        name="Home Mortgage",
        apr=3.5,
        og_principal=320000.0,
        tenure=360,
    )

    # Act
    loan = debt_config.to_loan()

    # Assert
    assert isinstance(loan, Loan)
    assert loan.type_ == DebtType.HOUSE
    assert loan.name == "Home Mortgage"
    assert loan.apr == 3.5
    assert loan.og_principal == 320000.0
    assert loan.tenure == 360


def test_account_config_to_account():
    """Test converting AccountConfig to Account"""
    # Arrange
    asset_config = AssetConfig(
        type_=AssetType.STOCKS,
        name="VTI",
        ticker="VTI",
        shares=100.0,
        cost_basis=200.0,
    )

    account_config = AccountConfig(
        institution="Vanguard",
        acc_type=AccountType.BROKERAGE,
        acc_holdings=[asset_config.to_asset()],
    )

    # Act
    account = account_config.to_account()

    # Assert
    assert isinstance(account, Account)
    assert account.institution == "Vanguard"
    assert account.account_type == AccountType.BROKERAGE


def test_load_portfolio_from_json(sample_portfolio_data):
    """Test loading full portfolio from JSON"""
    # Act
    portfolio = PortfolioConfig(**sample_portfolio_data)

    # Assert
    assert portfolio.name == "Personal Portfolio"
    assert portfolio.owner == "John Doe"
    assert len(portfolio.accounts) == 3
    assert portfolio.last_updated == datetime.fromisoformat("2025-10-06T19:30:00+00:00")


def test_portfolio_accounts_structure(sample_portfolio_data):
    """Test that portfolio accounts have correct structure"""
    # Arrange
    portfolio = PortfolioConfig(**sample_portfolio_data)

    # Act
    vanguard_account = portfolio.accounts[0]
    chase_account = portfolio.accounts[1]
    fidelity_account = portfolio.accounts[2]

    # Assert - Vanguard account
    assert vanguard_account.institution == "Vanguard"
    assert vanguard_account.acc_type == AccountType.BROKERAGE
    assert len(vanguard_account.acc_holdings) == 2

    # Assert - Chase account
    assert chase_account.institution == "Chase"
    assert chase_account.acc_type == AccountType.BANK
    assert chase_account.acc_holdings is None

    # Assert - Fidelity account
    assert fidelity_account.institution == "Fidelity"
    assert fidelity_account.acc_type == AccountType.BROKERAGE
    assert len(fidelity_account.acc_holdings) == 1


def test_portfolio_asset_details(sample_portfolio_data):
    """Test that assets within accounts have correct details"""
    # Arrange
    portfolio = PortfolioConfig(**sample_portfolio_data)
    vanguard_account = portfolio.accounts[0]

    # Act
    vti_asset = vanguard_account.acc_holdings[0]
    bnd_asset = vanguard_account.acc_holdings[1]

    # Assert - VTI
    assert vti_asset.ticker == "VTI"
    assert vti_asset.type_ == AssetType.STOCKS
    assert vti_asset.shares == 100.5
    assert vti_asset.cost_basis == 200.0

    # Assert - BND
    assert bnd_asset.ticker == "BND"
    assert bnd_asset.type_ == AssetType.BONDS
    assert bnd_asset.shares == 50.0
    assert bnd_asset.cost_basis == 80.0


def test_convert_account_config_to_account_instance(sample_portfolio_data):
    """Test converting AccountConfig to actual Account instance"""
    # Arrange
    portfolio = PortfolioConfig(**sample_portfolio_data)
    vanguard_config = portfolio.accounts[0]

    # Act
    vanguard_account = vanguard_config.to_account()

    # Assert
    assert isinstance(vanguard_account, Account)
    assert vanguard_account.institution == "Vanguard"
    assert vanguard_account.account_type == AccountType.BROKERAGE


def test_portfolio_config_validation_invalid_account_type():
    """Test that invalid account type raises validation error"""
    # Arrange
    invalid_data = {
        "name": "Test Portfolio",
        "owner": "Jane Doe",
        "accounts": [
            {
                "institution": "Test Bank",
                "acc_type": "invalid_type",  # Invalid
                "acc_holdings": None,
            }
        ],
    }

    # Act & Assert
    with pytest.raises(ValueError):
        PortfolioConfig(**invalid_data)


def test_portfolio_config_validation_invalid_asset_type():
    """Test that invalid asset type raises validation error"""
    # Arrange
    invalid_data = {
        "name": "Test Portfolio",
        "owner": "Jane Doe",
        "accounts": [
            {
                "institution": "Vanguard",
                "acc_type": "brokerage",
                "acc_holdings": [
                    {
                        "type_": "invalid_asset_type",  # Invalid
                        "name": "Test",
                        "ticker": "TEST",
                        "shares": 10,
                    }
                ],
            }
        ],
    }

    # Act & Assert
    with pytest.raises(ValueError):
        PortfolioConfig(**invalid_data)
