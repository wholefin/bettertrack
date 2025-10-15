from pathlib import Path

import rich
import typer
from typing_extensions import Annotated

from bettertrack._constants import DEFAULT_PORTFOLIO_PATH
from bettertrack.config.portfolio import AccountConfig, PortfolioConfig
from bettertrack.core.accounts import AccountType

accounts_app = typer.Typer(help="Manage accounts")


@accounts_app.command("list")
def accounts_list():
    """
    List all accounts with their balances.
    """
    typer.echo("TODO: List accounts")


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
    if not portfolio_file.exists():
        rich.print(
            "[red]Error:[/red] Portfolio not found. Run [bold]bettertrack init[/bold] first."
        )
        raise typer.Exit(code=1)

    portfolio = PortfolioConfig.model_validate_json(portfolio_file.read_text())

    # Prompt for account details
    rich.print("\n[bold cyan]Add New Account[/bold cyan]\n")

    institution = typer.prompt("Institution name (e.g., Vanguard, Chase)")

    # Show available account types
    rich.print("\nAccount types:")
    for i, acc_type in enumerate(AccountType, 1):
        rich.print(f"  {i}. {acc_type.value}")

    acc_type_choice = typer.prompt("Select account type", type=int, default=1)
    acc_type = list(AccountType)[acc_type_choice - 1]

    cash = typer.prompt("Initial cash balance", type=float, default=0.0)

    # Create account config
    account_config = AccountConfig(
        institution=institution,
        acc_type=acc_type,
        cash=cash,
        acc_holdings=None,
    )

    # Add to portfolio
    if portfolio.accounts is None:
        portfolio.accounts = []
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
