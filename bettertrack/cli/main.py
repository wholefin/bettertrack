from pathlib import Path

import rich
import typer
from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated

from bettertrack._constants import DEFAULT_PORTFOLIO_PATH
from bettertrack.core.portfolio import Portfolio
from bettertrack.cli.accounts import accounts_app
from bettertrack.cli.holdings import holdings_app

app = typer.Typer(
    name="bettertrack",
    help="Networth and portfolio tracking CLI tool",
    no_args_is_help=True,
)

# Register sub-apps for command groups
app.add_typer(accounts_app, name="accounts")
app.add_typer(holdings_app, name="holdings")


# ============================================================================
# Main Commands
# ============================================================================


@app.command()
def init(
    portfolio_name: Annotated[str, typer.Option("--name", "-n", prompt=True)],
    owner_name: Annotated[str, typer.Option("--owner", "-o", prompt=True)],
    path: Annotated[Path, typer.Option("--path", "-p")] = DEFAULT_PORTFOLIO_PATH,
    force: Annotated[bool, typer.Option("--force", "-f")] = False,
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

    conf = Portfolio(name=portfolio_name, owner=owner_name)
    conf.save(path / "portfolio.json")

    rich.print(f"Initialized portfolio at {path} for {owner_name}'s '{portfolio_name}'")


@app.command()
def ls(path: Annotated[Path, typer.Option("--path", "-p")] = DEFAULT_PORTFOLIO_PATH):
    """
    List all portfolios.
    """
    portfolio_files = list(path.glob("*/portfolio.json"))
    if path.joinpath("portfolio.json").exists():
        portfolio_files.insert(0, path / "portfolio.json")

    if not portfolio_files:
        rich.print(
            "[yellow]No portfolios found. Run [bold]bettertrack init[/bold] to create one.[/yellow]"
        )
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan")
    table.add_column("Owner", style="green")
    table.add_column("Accounts", justify="right", style="magenta")
    table.add_column("Created", style="dim")
    table.add_column("Last Updated", style="dim")

    for pf in portfolio_files:
        portfolio = Portfolio.model_validate_json(pf.read_text())
        table.add_row(
            portfolio.name,
            portfolio.owner,
            str(len(portfolio.accounts)) if portfolio.accounts else "0",
            portfolio.created_at.strftime("%Y-%m-%d"),
            portfolio.last_updated.strftime("%Y-%m-%d %H:%M"),
        )

    Console().print(table)


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
# Entry Point
# ============================================================================


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
