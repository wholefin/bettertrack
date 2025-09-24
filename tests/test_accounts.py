import pytest
from bettertrack import AssetAccount, Holding
from bettertrack.accounts import Account, AccountType
from bettertrack.exceptions import OutOfCashError


def test_account():
    """
    Test the Account class.
    """
    account = Account("Capital One", AccountType.BANK)
    assert account.institution == "Capital One"
    assert account.account_type == AccountType.BANK


def test_asset_account_initialization():
    # Arrange & Act
    asset_account = AssetAccount("Vanguard", AccountType.BROKERAGE)

    # Assert
    assert asset_account.institution == "Vanguard"
    assert asset_account.account_type == AccountType.BROKERAGE
    assert asset_account.cash == 0.0
    assert asset_account.holdings == []


def test_buy_with_insufficient_cash(mocker):
    # Arrange
    asset_account = AssetAccount("Vanguard", AccountType.BROKERAGE)
    mock_holding = mocker.Mock(spec=Holding)
    mock_holding.ticker = "VTI"

    # Mock the get_asset_price function
    mocker.patch("bettertrack.accounts.get_asset_price", return_value=100.0)

    # Act & Assert
    with pytest.raises(OutOfCashError):
        asset_account.buy(1000.0, mock_holding)
