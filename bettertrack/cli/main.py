from pathlib import Path

import rich
import typer
from typing_extensions import Annotated

from bettertrack._constants import DEFAULT_PORTFOLIO_PATH
from bettertrack.config.portfolio import PortfolioConfig
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
# Entry Point
# ============================================================================


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
