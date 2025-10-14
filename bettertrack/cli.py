from pathlib import Path

import rich
import typer
from typing_extensions import Annotated

from bettertrack._constants import DEFAULT_PORTFOLIO_PATH
from bettertrack.config.portfolio import PortfolioConfig

app = typer.Typer(
    name="bettertrack",
    help="Networth and portfolio tracking CLI tool",
    no_args_is_help=True,
)

# Create sub-apps for command groups
accounts_app = typer.Typer(help="Manage accounts")
holdings_app = typer.Typer(help="Manage holdings")
app.add_typer(accounts_app, name="accounts")
app.add_typer(holdings_app, name="holdings")


# ============================================================================
# Main Commands
# ============================================================================


@app.command()
def init(
    path: Annotated[Path, typer.Option("--path", "-p")] = DEFAULT_PORTFOLIO_PATH,
    force: Annotated[bool, typer.Option("--force", "-f")] = False,
    portfolio_name: Annotated[
        str, typer.Option("--name", "-n", prompt_required=True)
    ] = "My Portfolio",
    owner_name: Annotated[
        str, typer.Option("--owner", "-o", prompt_required=True)
    ] = "User",
):
    """
    Initialize a new portfolio at the specified path.

    Creates a portfolio.json file in ~/.bettertrack by default.
    If the directory already exists, use --force to overwrite.
    """
    if path.exists():
        rich.print(f"Portfolio path already exists at {path}")
        if not force:
            rich.print(
                "Use [bold blue]--force[/bold blue] to overwrite existing portfolio."
            )
            raise typer.Exit(code=1)

    path.mkdir(parents=True, exist_ok=True)

    conf = PortfolioConfig(name=portfolio_name, owner=owner_name)
    conf.save(path / "portfolio.json")

    rich.print(f"Initialized portfolio at {path} for {owner_name}'s '{portfolio_name}'")


@app.command()
def status():
    """
    Show quick portfolio status (net worth, total assets, total debts).
    """
    typer.echo("TODO: Implement status command")


@app.command()
def networth():
    """
    Calculate and display detailed net worth breakdown by account.
    """
    typer.echo("TODO: Implement networth command")


@app.command()
def update(
    ticker: Annotated[
        str, typer.Option("--ticker", "-t", help="Update specific ticker only")
    ] = None,
):
    """
    Fetch latest prices for all holdings (or specific ticker).

    Updates portfolio.json with current market prices from Alpha Vantage.
    """
    if ticker:
        typer.echo(f"TODO: Update price for {ticker}")
    else:
        typer.echo("TODO: Update all prices")


@app.command()
def config(
    key: Annotated[str, typer.Argument(help="Config key to view/set")] = None,
    value: Annotated[str, typer.Argument(help="Config value to set")] = None,
):
    """
    View or set configuration values.

    Examples:
        bettertrack config                    # Show all config
        bettertrack config ALPHAVANTAGE_API_KEY your_key_here
    """
    if key and value:
        typer.echo(f"TODO: Set {key} = {value}")
    elif key:
        typer.echo(f"TODO: Show value for {key}")
    else:
        typer.echo("TODO: Show all config")


# ============================================================================
# Accounts Commands
# ============================================================================


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
    from bettertrack.config.portfolio import AccountConfig
    from bettertrack.core.accounts import AccountType

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
        f"\n[green]✓[/green] Added {institution} ({acc_type.value}) with ${cash:,.2f} cash"
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


# ============================================================================
# Holdings Commands
# ============================================================================


@holdings_app.command("list")
def holdings_list(
    account_id: Annotated[
        str, typer.Option("--account", "-a", help="Filter by account ID")
    ] = None,
):
    """
    List all holdings, optionally filtered by account.
    """
    if account_id:
        typer.echo(f"TODO: List holdings for account {account_id}")
    else:
        typer.echo("TODO: List all holdings")


@holdings_app.command("add")
def holdings_add(
    account_id: Annotated[str, typer.Argument(help="Account ID to add holding to")],
):
    """
    Add a new holding to an account (interactive).

    Prompts for ticker, shares, cost basis, etc.
    """
    typer.echo(f"TODO: Add holding to account {account_id}")


@holdings_app.command("remove")
def holdings_remove(
    account_id: Annotated[str, typer.Argument(help="Account ID")],
    ticker: Annotated[str, typer.Argument(help="Ticker symbol to remove")],
):
    """
    Remove a holding from an account.
    """
    typer.echo(f"TODO: Remove {ticker} from account {account_id}")


# ============================================================================
# Entry Point
# ============================================================================


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
