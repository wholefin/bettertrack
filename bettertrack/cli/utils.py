import typer
from rich.console import Console
from rich.table import Table
from rich import print

from bettertrack.config.portfolio import AccountConfig
from bettertrack.core.accounts import AccountType


def display_accounts_table(accounts: list[AccountConfig]) -> None:
    """
    Display a table of accounts using rich.

    Parameters
    ----------
    accounts : list[Account]
        A list of Account instances to display.
    """
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Institution", style="magenta")
    table.add_column("Type", style="green")
    table.add_column("Cash Balance", justify="right", style="yellow")
    table.add_column("Total Value", justify="right", style="yellow")

    for idx, account in enumerate(accounts, 1):
        cash_balance = f"${account.cash:,.2f}" if hasattr(account, "cash") else "N/A"

        # TODO: Support total amount
        total_value = f"${account.cash:,.2f}"
        table.add_row(
            str(idx),
            account.institution,
            account.acc_type,
            cash_balance,
            total_value,
        )

    console = Console()
    console.print(table)


def check_if_portfolio_exists(portfolio_file) -> None:
    """
    Check if the portfolio file exists. If not, print an error message and exit.

    Parameters
    ----------
    portfolio_file : Path
        The path to the portfolio file.
    """
    if not portfolio_file.exists():
        print(
            "[red]Error:[/red] Portfolio not found. Run [bold]bettertrack init[/bold] first."
        )
        raise typer.Exit(code=1)


def select_asset_or_debt() -> bool:
    """
    Prompt the user to select whether the account is an asset or a debt.

    Returns
    -------
    bool
        True if the account is an asset, False if it is a debt/liability.
    """
    # Show asset/liability options
    print("\nAsset or Liability:")
    print("  1. Asset")
    print("  2. Liability")

    asset_or_liability_choice = typer.prompt(
        "Select (1 for Asset, 2 for Liability)", type=int, default=1
    )
    is_asset = asset_or_liability_choice == 1

    if is_asset:
        print("\nAdding as Asset account.")
        print("Enter holdings later using the 'holdings add' command.")
    else:
        print("\nAdding as Liability account.")
        print("Enter loans later using the 'holdings add' command.")

    return is_asset


def select_account_type() -> AccountType:
    print("\nAccount types:")
    for i, acc_type in enumerate(AccountType, 1):
        print(f"  {i}. {acc_type.value}")

    acc_type_choice = typer.prompt("Select account type", type=int, default=1)
    acc_type = list(AccountType)[acc_type_choice - 1]
    return AccountType(acc_type)
