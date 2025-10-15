import typer
from rich.console import Console
from rich.table import Table
from rich import print

from bettertrack.config.portfolio import AccountConfig


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
        total_value = f"${account.total_amount:,.2f}"
        table.add_row(
            str(idx),
            account.institution,
            account.account_type.value,
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
