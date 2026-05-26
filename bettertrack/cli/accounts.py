from pathlib import Path

import rich
import typer
from typing_extensions import Annotated

from bettertrack._constants import DEFAULT_PORTFOLIO_PATH
from bettertrack.cli.utils import (
    display_accounts_table,
    display_holdings_table,
    get_account_or_exit,
    load_portfolio,
    select_account_type,
    select_asset_or_debt,
)
from bettertrack.core.accounts import Account, AccountType

accounts_app = typer.Typer(help="Manage accounts", no_args_is_help=True)


@accounts_app.command("ls")
def accounts_list(
    path: Annotated[Path, typer.Option("--path", "-p")] = DEFAULT_PORTFOLIO_PATH,
) -> None:
    """List all accounts with their balances."""
    _, portfolio = load_portfolio(path)

    if not portfolio.accounts:
        rich.print("[yellow]No accounts found in portfolio.[/yellow]")
        return

    display_accounts_table(portfolio.accounts)


@accounts_app.command("add")
def accounts_add(
    path: Annotated[Path, typer.Option("--path", "-p")] = DEFAULT_PORTFOLIO_PATH,
):
    """Add a new account interactively."""
    portfolio_file, portfolio = load_portfolio(path)

    rich.print("\n[bold cyan]Add New Account[/bold cyan]\n")
    institution = typer.prompt("Institution name (e.g., Vanguard, Chase)")
    is_asset = select_asset_or_debt()
    cash = (
        typer.prompt("Current cash balance", type=float, default=0.0)
        if is_asset
        else 0.0
    )
    acc_type = select_account_type(is_asset)

    if portfolio.accounts is None:
        portfolio.accounts = []

    account = Account(
        account_id=len(portfolio.accounts) + 1,
        institution=institution,
        acc_type=acc_type,
        cash=cash,
        acc_holdings=None,
        is_asset=is_asset,
    )
    portfolio.accounts.append(account)
    portfolio.save(portfolio_file)

    rich.print(
        f"\n[green]Added[/green] {institution} ({acc_type.value}) with ${cash:,.2f} cash"
    )
    rich.print(f"Portfolio now has {len(portfolio.accounts)} account(s)")


@accounts_app.command("update")
def accounts_update(
    account_id: Annotated[int, typer.Argument(help="Account ID to update")],
    path: Annotated[Path, typer.Option("--path", "-p")] = DEFAULT_PORTFOLIO_PATH,
    institution: Annotated[
        str, typer.Option("--institution", "-i", help="New institution name")
    ] = None,
    cash: Annotated[
        float, typer.Option("--cash", "-c", help="New cash balance")
    ] = None,
    acc_type: Annotated[
        AccountType, typer.Option("--type", "-t", help="New account type")
    ] = None,
):
    """
    Update an existing account's fields.

    Pass flags to update non-interactively, or run with no flags to be prompted.
    """
    portfolio_file, portfolio = load_portfolio(path)
    account = get_account_or_exit(portfolio, account_id)

    interactive = institution is None and cash is None and acc_type is None

    if interactive:
        rich.print(
            f"\n[bold cyan]Updating account #{account.account_id}[/bold cyan] "
            f"([magenta]{account.institution}[/magenta])\n"
        )
        institution = typer.prompt("Institution", default=account.institution)
        rich.print(f"\nCurrent type: [green]{account.acc_type.value}[/green]")
        if typer.confirm("Change account type?", default=False):
            acc_type = select_account_type(account.is_asset)
        if account.is_asset:
            cash = typer.prompt("Cash balance", type=float, default=account.cash)

    if cash is not None and not account.is_asset:
        rich.print("[red]Cannot set cash on a liability account.[/red]")
        raise typer.Exit(code=1)

    if institution is not None:
        account.institution = institution
    if acc_type is not None:
        account.acc_type = acc_type
    if cash is not None:
        account.cash = cash

    portfolio.save(portfolio_file)
    rich.print(
        f"[green]Updated[/green] account #{account.account_id} "
        f"({account.institution}, ${account.cash:,.2f})"
    )


@accounts_app.command("remove")
def accounts_remove(
    account_id: Annotated[int, typer.Argument(help="Account ID to remove")],
    path: Annotated[Path, typer.Option("--path", "-p")] = DEFAULT_PORTFOLIO_PATH,
    yes: Annotated[bool, typer.Option("--yes", "-y", help="Skip confirmation")] = False,
):
    """Remove an account from portfolio."""
    portfolio_file, portfolio = load_portfolio(path)
    account = get_account_or_exit(portfolio, account_id)

    if not yes and not typer.confirm(
        f"Remove {account.institution} ({account.acc_type.value})?"
    ):
        rich.print("[yellow]Aborted.[/yellow]")
        raise typer.Exit(code=0)

    portfolio.accounts = [a for a in portfolio.accounts if a.account_id != account_id]
    # Keep account_id contiguous after removal.
    for new_id, acc in enumerate(portfolio.accounts, 1):
        acc.account_id = new_id

    portfolio.save(portfolio_file)
    rich.print(
        f"[green]Removed[/green] {account.institution} ({account.acc_type.value})"
    )


@accounts_app.command("show")
def accounts_show(
    account_id: Annotated[int, typer.Argument(help="Account ID to show")],
    path: Annotated[Path, typer.Option("--path", "-p")] = DEFAULT_PORTFOLIO_PATH,
):
    """Show detailed information for a specific account."""
    _, portfolio = load_portfolio(path)
    account = get_account_or_exit(portfolio, account_id)

    kind = "Asset" if account.is_asset else "Liability"
    kind_color = "green" if account.is_asset else "red"
    holdings = account.acc_holdings or []

    rich.print(f"\n[bold cyan]Account #{account.account_id}[/bold cyan]")
    rich.print(f"  Institution: [magenta]{account.institution}[/magenta]")
    rich.print(f"  Type:        [green]{account.acc_type.value}[/green]")
    rich.print(f"  Kind:        [{kind_color}]{kind}[/{kind_color}]")
    rich.print(f"  Cash:        [yellow]${account.cash:,.2f}[/yellow]")
    rich.print(f"  Holdings:    {len(holdings)}")
    display_holdings_table(account)
