import typer
from typing_extensions import Annotated

holdings_app = typer.Typer(help="Manage holdings")


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
