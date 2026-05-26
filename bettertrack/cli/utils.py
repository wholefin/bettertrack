from enum import Enum
from pathlib import Path

import typer
from rich import print
from rich.console import Console
from rich.table import Table

from bettertrack.core.accounts import Account, AccountType
from bettertrack.core.portfolio import Portfolio
from bettertrack.core.assets import AssetType
from bettertrack.core.debts import LiabilityType


def check_if_portfolio_exists(portfolio_file: Path) -> None:
    """Exit with an error message if `portfolio_file` does not exist."""
    if not portfolio_file.exists():
        print(
            "[red]Error:[/red] Portfolio not found. "
            "Run [bold]bettertrack init[/bold] first."
        )
        raise typer.Exit(code=1)


def load_portfolio(path: Path) -> tuple[Path, Portfolio]:
    """Load a portfolio from `<path>/portfolio.json`, exiting if missing."""
    portfolio_file = path / "portfolio.json"
    check_if_portfolio_exists(portfolio_file)
    return portfolio_file, Portfolio.model_validate_json(portfolio_file.read_text())


def get_account_or_exit(portfolio: Portfolio, account_id: int) -> Account:
    """Look up an account by id, or print an error and exit."""
    account = next(
        (a for a in (portfolio.accounts or []) if a.account_id == account_id), None
    )
    if account is None:
        print(f"[red]Account with ID {account_id} not found.[/red]")
        raise typer.Exit(code=1)
    return account


def get_holding_or_exit(account: Account, holding_index: int):
    """Look up a holding by 1-based index within an account, or exit."""
    holdings = account.acc_holdings or []
    if not 1 <= holding_index <= len(holdings):
        print(
            f"[red]Holding index {holding_index} out of range "
            f"(1..{len(holdings)}) for account #{account.account_id}.[/red]"
        )
        raise typer.Exit(code=1)
    return holdings[holding_index - 1]


def _select_enum(label: str, options: list[Enum]) -> Enum:
    print(f"\n{label}:")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt.value}")
    choice = typer.prompt("Select", type=int, default=1)
    return options[choice - 1]


def select_asset_or_debt() -> bool:
    """Prompt whether the new account is an asset (True) or a liability (False)."""
    is_asset = typer.confirm("Is this an asset account? (No = liability)", default=True)
    kind = "Asset" if is_asset else "Liability"
    print(
        f"\nAdding as {kind} account. "
        f"Enter holdings later with the 'holdings add' command."
    )
    return is_asset


def select_account_type(is_asset: bool) -> AccountType:
    options = (
        AccountType.get_asset_types() if is_asset else AccountType.get_liability_types()
    )
    return _select_enum("Account types", options)


def select_asset_type() -> AssetType:
    return _select_enum("Asset types", list(AssetType))


def select_liability_type() -> LiabilityType:
    return _select_enum("Liability types", list(LiabilityType))


def display_accounts_table(accounts: list[Account]) -> None:
    """Render a list of accounts as a rich table."""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Institution", style="magenta")
    table.add_column("Type", style="green")
    table.add_column("Cash Balance", justify="right", style="yellow")
    table.add_column("Total Value", justify="right", style="yellow")

    for account in accounts:
        # TODO: Support total amount (not just cash)
        cash = f"${account.cash:,.2f}"
        table.add_row(
            str(account.account_id),
            account.institution,
            account.acc_type.value,
            cash,
            cash,
        )

    Console().print(table)


def display_holdings_table(account: Account) -> None:
    """
    Render an account's holdings as a rich table.

    Asset accounts get share/cost-basis columns; liability accounts get
    principal/APR/tenure columns.
    """
    holdings = account.acc_holdings or []
    if not holdings:
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", justify="right", style="cyan", no_wrap=True)
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Details", style="yellow")

    for idx, h in enumerate(holdings, 1):
        if account.is_asset:
            cost = h.cost_basis if h.cost_basis is not None else 0.0
            details = f"{h.shares} shares @ ${cost:,.2f}"
        else:
            details = f"${h.og_principal:,.2f} @ {h.apr}% / {h.tenure}mo"
        table.add_row(str(idx), h.name, h.type_.value, details)

    Console().print(table)
