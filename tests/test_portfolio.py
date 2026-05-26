import json
from datetime import datetime
from pathlib import Path

import pytest

from bettertrack.core.accounts import Account, AccountType
from bettertrack.core.assets import Asset, AssetType
from bettertrack.core.debts import Liability, LiabilityType
from bettertrack.core.portfolio import Portfolio


@pytest.fixture
def sample_portfolio_path():
    return Path(__file__).parent / "fixtures" / "sample_portfolio.json"


@pytest.fixture
def sample_portfolio_data(sample_portfolio_path):
    with open(sample_portfolio_path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# JSON round-trip / loading
# ---------------------------------------------------------------------------


def test_load_portfolio_from_json(sample_portfolio_data):
    portfolio = Portfolio(**sample_portfolio_data)

    assert portfolio.name == "Personal Portfolio"
    assert portfolio.owner == "John Doe"
    assert len(portfolio.accounts) == 6
    assert portfolio.last_updated == datetime.fromisoformat("2025-10-13T12:00:00+00:00")


def test_portfolio_json_round_trip(sample_portfolio_data):
    """A model serialized then reparsed equals the original."""
    portfolio = Portfolio(**sample_portfolio_data)
    raw = portfolio.model_dump_json()
    reparsed = Portfolio.model_validate_json(raw)
    assert reparsed == portfolio


def test_portfolio_accounts_structure(sample_portfolio_data):
    portfolio = Portfolio(**sample_portfolio_data)

    vanguard, chase, fidelity = portfolio.accounts[:3]

    assert vanguard.institution == "Vanguard"
    assert vanguard.acc_type == AccountType.BROKERAGE
    assert vanguard.is_asset is True
    assert len(vanguard.acc_holdings) == 2

    assert chase.institution == "Chase"
    assert chase.acc_type == AccountType.BANK
    assert chase.acc_holdings is None

    assert fidelity.institution == "Fidelity"
    assert len(fidelity.acc_holdings) == 1


def test_holdings_routed_to_correct_type(sample_portfolio_data):
    """Asset accounts get Asset holdings; liability accounts get Liability."""
    portfolio = Portfolio(**sample_portfolio_data)
    for account in portfolio.accounts:
        for holding in account.acc_holdings or []:
            if account.is_asset:
                assert isinstance(holding, Asset)
            else:
                assert isinstance(holding, Liability)


def test_portfolio_asset_details(sample_portfolio_data):
    portfolio = Portfolio(**sample_portfolio_data)
    vti, bnd = portfolio.accounts[0].acc_holdings

    assert vti.ticker == "VTI"
    assert vti.type_ == AssetType.STOCKS
    assert vti.shares == 100.5
    assert vti.cost_basis == 200.0

    assert bnd.ticker == "BND"
    assert bnd.type_ == AssetType.BONDS


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def test_invalid_account_type_rejected():
    bad = {
        "name": "T",
        "owner": "J",
        "accounts": [
            {
                "account_id": 1,
                "institution": "X",
                "acc_type": "invalid_type",
                "acc_holdings": None,
            }
        ],
    }
    with pytest.raises(ValueError):
        Portfolio(**bad)


def test_invalid_asset_type_rejected():
    bad = {
        "name": "T",
        "owner": "J",
        "accounts": [
            {
                "account_id": 1,
                "institution": "Vanguard",
                "acc_type": "brokerage",
                "is_asset": True,
                "acc_holdings": [
                    {
                        "type_": "invalid_asset_type",
                        "name": "Test",
                        "ticker": "TEST",
                        "shares": 10,
                    }
                ],
            }
        ],
    }
    with pytest.raises(ValueError):
        Portfolio(**bad)


# ---------------------------------------------------------------------------
# Asset.__add__ (weighted cost-basis combine) and __eq__ (ticker-only)
# ---------------------------------------------------------------------------


def test_asset_add_weighted_cost_basis():
    a = Asset(
        type_=AssetType.STOCKS, name="VOO", ticker="VOO", shares=10, cost_basis=400.0
    )
    b = Asset(
        type_=AssetType.STOCKS, name="VOO", ticker="VOO", shares=10, cost_basis=500.0
    )
    combined = a + b
    assert combined.shares == 20
    assert combined.cost_basis == 450.0
    # Source operands unchanged
    assert a.shares == 10
    assert a.cost_basis == 400.0


def test_asset_add_zero_shares_returns_other():
    empty = Asset(type_=AssetType.STOCKS, name="VOO", ticker="VOO", shares=0)
    other = Asset(
        type_=AssetType.STOCKS, name="VOO", ticker="VOO", shares=5, cost_basis=300
    )
    assert (empty + other) is other


def test_asset_add_ticker_mismatch():
    a = Asset(
        type_=AssetType.STOCKS, name="VOO", ticker="VOO", shares=10, cost_basis=400.0
    )
    b = Asset(
        type_=AssetType.STOCKS, name="QQQ", ticker="QQQ", shares=10, cost_basis=400.0
    )
    with pytest.raises(TypeError):
        a + b


def test_asset_eq_is_ticker_only():
    a = Asset(
        type_=AssetType.STOCKS, name="VOO", ticker="VOO", shares=10, cost_basis=400.0
    )
    b = Asset(
        type_=AssetType.STOCKS, name="VOO", ticker="VOO", shares=99, cost_basis=999.0
    )
    assert a == b


def test_asset_is_unhashable():
    a = Asset(type_=AssetType.STOCKS, name="VOO", ticker="VOO", shares=10)
    with pytest.raises(TypeError):
        hash(a)


# ---------------------------------------------------------------------------
# Liability shape
# ---------------------------------------------------------------------------


def test_liability_construction():
    loan = Liability(
        type_=LiabilityType.HOUSE,
        name="Home Mortgage",
        apr=3.5,
        og_principal=320000.0,
        tenure=360,
    )
    assert loan.type_ == LiabilityType.HOUSE
    assert loan.og_principal == 320000.0


# ---------------------------------------------------------------------------
# Account direct construction (no more to_account())
# ---------------------------------------------------------------------------


def test_account_with_holdings_constructs_directly():
    asset = Asset(
        type_=AssetType.STOCKS, name="VTI", ticker="VTI", shares=100, cost_basis=200
    )
    account = Account(
        account_id=1,
        institution="Vanguard",
        acc_type=AccountType.BROKERAGE,
        is_asset=True,
        cash=1000.0,
        acc_holdings=[asset],
    )
    assert account.institution == "Vanguard"
    assert account.acc_type == AccountType.BROKERAGE
    assert account.cash == 1000.0
    assert len(account.acc_holdings) == 1
    assert isinstance(account.acc_holdings[0], Asset)
