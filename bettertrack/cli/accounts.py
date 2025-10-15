from pathlib import Path

import rich
import typer
from typing_extensions import Annotated

from bettertrack._constants import DEFAULT_PORTFOLIO_PATH
from bettertrack.cli.utils import (
    display_accounts_table,
    check_if_portfolio_exists,
    select_asset_or_debt,
    select_account_type,
)
from bettertrack.config.portfolio import AccountConfig, PortfolioConfig

accounts_app = typer.Typer(help="Manage accounts")


@accounts_app.command("list")
def accounts_list(
    path: Annotated[Path, typer.Option("--path", "-p")] = DEFAULT_PORTFOLIO_PATH,
) -> None:
    """
    List all accounts with their balances.
    """
    portfolio_file = path / "portfolio.json"

    # Load existing portfolio
    check_if_portfolio_exists(portfolio_file)

    portfolio = PortfolioConfig.model_validate_json(portfolio_file.read_text())

    if not portfolio.accounts:
        rich.print("[yellow]No accounts found in portfolio.[/yellow]")
        raise typer.Exit(code=0)

    display_accounts_table(portfolio.accounts)


@accounts_app.command("add")
def accounts_add(
    path: Annotated[Path, typer.Option("--path", "-p")] = DEFAULT_PORTFOLIO_PATH,
):
    """
    Add a new account (interactive).

    Prompts for account details and adds to portfolio.
    """
    portfolio_file = path / "portfolio.json"

    # Load existing portfolio
    check_if_portfolio_exists(portfolio_file)

    portfolio = PortfolioConfig.model_validate_json(portfolio_file.read_text())

    # Prompt for account details
    rich.print("\n[bold cyan]Add New Account[/bold cyan]\n")

    institution = typer.prompt("Institution name (e.g., Vanguard, Chase)")

    # Show asset/liability options
    is_asset = select_asset_or_debt()
    if is_asset:
        cash = typer.prompt("Current cash balance", type=float, default=0.0)
    else:
        cash = 0.0

    # Show available account types
    acc_type = select_account_type()

    # Add to portfolio
    if portfolio.accounts is None:
        portfolio.accounts = []

    # Determine account_id based on order (1-indexed)
    account_id = len(portfolio.accounts) + 1

    # Create account config
    account_config = AccountConfig(
        account_id=account_id,
        institution=institution,
        acc_type=acc_type,
        cash=cash,
        acc_holdings=None,
        is_asset=is_asset,
    )

    portfolio.accounts.append(account_config)

    # Save
    portfolio.save(portfolio_file)

    rich.print(
        f"\n[green][/green] Added {institution} ({acc_type.value}) with ${cash:,.2f} cash"
    )
    rich.print(f"Portfolio now has {len(portfolio.accounts)} account(s)")


@accounts_app.command("remove")
def accounts_remove(
    account_id: Annotated[str, typer.Argument(help="Account ID to remove")],
):
    """
    Remove an account from portfolio.
    """
    typer.echo(f"TODO: Remove account {account_id}")


@accounts_app.command("show")
def accounts_show(
    account_id: Annotated[str, typer.Argument(help="Account ID to show")],
):
    """
    Show detailed information for a specific account.
    """
    typer.echo(f"TODO: Show account {account_id}")
