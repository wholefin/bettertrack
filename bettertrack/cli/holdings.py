from pathlib import Path

import rich
import typer
from typing_extensions import Annotated

from bettertrack._constants import DEFAULT_PORTFOLIO_PATH
from bettertrack.cli.utils import (
    display_holdings_table,
    get_account_or_exit,
    get_holding_or_exit,
    load_portfolio,
    select_asset_type,
    select_liability_type,
)
from bettertrack.core.accounts import Account
from bettertrack.core.assets import Asset, AssetType
from bettertrack.core.debts import Liability, LiabilityType

holdings_app = typer.Typer(help="Manage holdings", no_args_is_help=True)

_ASSET_ONLY_FLAGS = (
    "--ticker",
    "--shares",
    "--cost-basis",
    "--yield",
    "--expense-ratio",
)
_LIABILITY_ONLY_FLAGS = ("--apr", "--principal", "--tenure")


def _reject_wrong_kind_flags(
    account: Account,
    asset_values: tuple,
    liability_values: tuple,
) -> None:
    """Exit if liability-only flags are set on an asset account, or vice versa."""
    if account.is_asset and any(v is not None for v in liability_values):
        rich.print(
            f"[red]{'/'.join(_LIABILITY_ONLY_FLAGS)} are for liability accounts only.[/red]"
        )
        raise typer.Exit(code=1)
    if not account.is_asset and any(v is not None for v in asset_values):
        rich.print(
            f"[red]{'/'.join(_ASSET_ONLY_FLAGS)} are for asset accounts only.[/red]"
        )
        raise typer.Exit(code=1)


def _print_account_header(account: Account) -> None:
    kind = "Asset" if account.is_asset else "Liability"
    kind_color = "green" if account.is_asset else "red"
    rich.print(
        f"\n[bold cyan]#{account.account_id} {account.institution}[/bold cyan] "
        f"([green]{account.acc_type.value}[/green], "
        f"[{kind_color}]{kind}[/{kind_color}])"
    )


@holdings_app.command("ls")
def holdings_list(
    account_id: Annotated[
        int, typer.Option("--account", "-a", help="Filter by account ID")
    ] = None,
    path: Annotated[Path, typer.Option("--path", "-p")] = DEFAULT_PORTFOLIO_PATH,
):
    """List all holdings, optionally filtered by account."""
    _, portfolio = load_portfolio(path)

    if account_id is not None:
        accounts = [get_account_or_exit(portfolio, account_id)]
    else:
        accounts = portfolio.accounts or []

    accounts_with_holdings = [a for a in accounts if a.acc_holdings]
    if not accounts_with_holdings:
        rich.print("[yellow]No holdings found.[/yellow]")
        return

    for account in accounts_with_holdings:
        _print_account_header(account)
        display_holdings_table(account)


@holdings_app.command("add")
def holdings_add(
    account_id: Annotated[int, typer.Argument(help="Account ID to add holding to")],
    path: Annotated[Path, typer.Option("--path", "-p")] = DEFAULT_PORTFOLIO_PATH,
    name: Annotated[str, typer.Option("--name", "-n")] = None,
    type_: Annotated[
        str, typer.Option("--type", "-t", help="AssetType or LiabilityType value")
    ] = None,
    # Asset-only
    ticker: Annotated[str, typer.Option("--ticker")] = None,
    shares: Annotated[float, typer.Option("--shares")] = None,
    cost_basis: Annotated[float, typer.Option("--cost-basis")] = None,
    yield_: Annotated[float, typer.Option("--yield")] = None,
    expense_ratio: Annotated[float, typer.Option("--expense-ratio")] = None,
    # Liability-only
    apr: Annotated[float, typer.Option("--apr")] = None,
    principal: Annotated[float, typer.Option("--principal")] = None,
    tenure: Annotated[int, typer.Option("--tenure")] = None,
):
    """
    Add a holding to an account.

    Run with no flags for an interactive prompt; pass flags for non-interactive use.
    """
    portfolio_file, portfolio = load_portfolio(path)
    account = get_account_or_exit(portfolio, account_id)

    asset_values = (ticker, shares, cost_basis, yield_, expense_ratio)
    liability_values = (apr, principal, tenure)
    _reject_wrong_kind_flags(account, asset_values, liability_values)

    interactive = all(
        v is None for v in (name, type_, *asset_values, *liability_values)
    )

    if account.is_asset:
        if interactive:
            rich.print(
                f"\n[bold cyan]Add holding to #{account.account_id} "
                f"{account.institution}[/bold cyan]\n"
            )
            asset_type = select_asset_type()
            name = typer.prompt("Name (e.g., Vanguard S&P 500)")
            ticker = typer.prompt("Ticker (e.g., VOO)")
            shares = typer.prompt("Shares", type=float, default=0.0)
            cost_basis = _prompt_optional_float("Cost basis per share")
            yield_ = _prompt_optional_float("Yield %")
            expense_ratio = typer.prompt("Expense ratio", type=float, default=0.0)
        else:
            asset_type = AssetType(type_) if type_ else None
            if asset_type is None or not name or not ticker or shares is None:
                rich.print(
                    "[red]--type, --name, --ticker, and --shares are required "
                    "for asset holdings.[/red]"
                )
                raise typer.Exit(code=1)
            expense_ratio = expense_ratio if expense_ratio is not None else 0.0

        holding = Asset(
            type_=asset_type,
            name=name,
            ticker=ticker,
            shares=shares,
            cost_basis=cost_basis,
            yield_=yield_,
            expense_ratio=expense_ratio,
        )
    else:
        if interactive:
            rich.print(
                f"\n[bold cyan]Add liability to #{account.account_id} "
                f"{account.institution}[/bold cyan]\n"
            )
            liability_type = select_liability_type()
            name = typer.prompt("Name (e.g., Toyota auto loan)")
            apr = typer.prompt("APR %", type=float)
            principal = typer.prompt("Original principal", type=float)
            tenure = typer.prompt("Tenure (months)", type=int)
        else:
            liability_type = LiabilityType(type_) if type_ else None
            if (
                liability_type is None
                or not name
                or apr is None
                or principal is None
                or tenure is None
            ):
                rich.print(
                    "[red]--type, --name, --apr, --principal, and --tenure are "
                    "required for liability holdings.[/red]"
                )
                raise typer.Exit(code=1)

        holding = Liability(
            type_=liability_type,
            name=name,
            apr=apr,
            og_principal=principal,
            tenure=tenure,
        )

    if account.acc_holdings is None:
        account.acc_holdings = []
    account.acc_holdings.append(holding)
    portfolio.save(portfolio_file)

    rich.print(
        f"\n[green]Added[/green] {holding.name} ({holding.type_.value}) to "
        f"#{account.account_id} {account.institution}"
    )


@holdings_app.command("show")
def holdings_show(
    account_id: Annotated[int, typer.Argument(help="Account ID")],
    holding_index: Annotated[int, typer.Argument(help="1-based holding index")],
    path: Annotated[Path, typer.Option("--path", "-p")] = DEFAULT_PORTFOLIO_PATH,
):
    """Show detailed information for a specific holding."""
    _, portfolio = load_portfolio(path)
    account = get_account_or_exit(portfolio, account_id)
    h = get_holding_or_exit(account, holding_index)

    def fmt_optional(value, formatter):
        return "[dim]—[/dim]" if value is None else formatter(value)

    rich.print(
        f"\n[bold cyan]Holding #{holding_index}[/bold cyan] "
        f"in #{account.account_id} {account.institution}"
    )
    rich.print(f"  Name:  [magenta]{h.name}[/magenta]")
    rich.print(f"  Type:  [green]{h.type_.value}[/green]")
    if account.is_asset:
        rich.print(f"  Ticker:        {h.ticker}")
        rich.print(f"  Shares:        {h.shares}")
        rich.print(
            f"  Cost basis:    {fmt_optional(h.cost_basis, lambda v: f'${v:,.2f}')}"
        )
        rich.print(f"  Yield:         {fmt_optional(h.yield_, lambda v: f'{v}%')}")
        rich.print(f"  Expense ratio: {h.expense_ratio}")
    else:
        rich.print(f"  APR:           {h.apr}%")
        rich.print(f"  Principal:     ${h.og_principal:,.2f}")
        rich.print(f"  Tenure:        {h.tenure} months")


@holdings_app.command("update")
def holdings_update(
    account_id: Annotated[int, typer.Argument(help="Account ID")],
    holding_index: Annotated[int, typer.Argument(help="1-based holding index")],
    path: Annotated[Path, typer.Option("--path", "-p")] = DEFAULT_PORTFOLIO_PATH,
    name: Annotated[str, typer.Option("--name", "-n")] = None,
    type_: Annotated[str, typer.Option("--type", "-t")] = None,
    ticker: Annotated[str, typer.Option("--ticker")] = None,
    shares: Annotated[float, typer.Option("--shares")] = None,
    cost_basis: Annotated[float, typer.Option("--cost-basis")] = None,
    yield_: Annotated[float, typer.Option("--yield")] = None,
    expense_ratio: Annotated[float, typer.Option("--expense-ratio")] = None,
    apr: Annotated[float, typer.Option("--apr")] = None,
    principal: Annotated[float, typer.Option("--principal")] = None,
    tenure: Annotated[int, typer.Option("--tenure")] = None,
):
    """
    Update fields on an existing holding.

    Pass flags to update non-interactively, or run with no flags to be prompted.
    """
    portfolio_file, portfolio = load_portfolio(path)
    account = get_account_or_exit(portfolio, account_id)
    h = get_holding_or_exit(account, holding_index)

    asset_values = (ticker, shares, cost_basis, yield_, expense_ratio)
    liability_values = (apr, principal, tenure)
    _reject_wrong_kind_flags(account, asset_values, liability_values)

    interactive = all(
        v is None for v in (name, type_, *asset_values, *liability_values)
    )

    if interactive:
        _interactive_update_in_place(account, h)
    else:
        # Flag-driven: only assign fields the user provided.
        if name is not None:
            h.name = name
        if type_ is not None:
            h.type_ = (AssetType if account.is_asset else LiabilityType)(type_)
        if account.is_asset:
            if ticker is not None:
                h.ticker = ticker
            if shares is not None:
                h.shares = shares
            if cost_basis is not None:
                h.cost_basis = cost_basis
            if yield_ is not None:
                h.yield_ = yield_
            if expense_ratio is not None:
                h.expense_ratio = expense_ratio
        else:
            if apr is not None:
                h.apr = apr
            if principal is not None:
                h.og_principal = principal
            if tenure is not None:
                h.tenure = tenure

    portfolio.save(portfolio_file)
    rich.print(
        f"[green]Updated[/green] holding #{holding_index} "
        f"({h.name}) in #{account.account_id} {account.institution}"
    )


@holdings_app.command("remove")
def holdings_remove(
    account_id: Annotated[int, typer.Argument(help="Account ID")],
    holding_index: Annotated[int, typer.Argument(help="1-based holding index")],
    path: Annotated[Path, typer.Option("--path", "-p")] = DEFAULT_PORTFOLIO_PATH,
    yes: Annotated[bool, typer.Option("--yes", "-y", help="Skip confirmation")] = False,
):
    """Remove a holding from an account."""
    portfolio_file, portfolio = load_portfolio(path)
    account = get_account_or_exit(portfolio, account_id)
    h = get_holding_or_exit(account, holding_index)

    if not yes and not typer.confirm(f"Remove {h.name} ({h.type_.value})?"):
        rich.print("[yellow]Aborted.[/yellow]")
        raise typer.Exit(code=0)

    del account.acc_holdings[holding_index - 1]
    portfolio.save(portfolio_file)

    rich.print(
        f"[green]Removed[/green] {h.name} from "
        f"#{account.account_id} {account.institution}"
    )


def _prompt_optional_float(label: str, current: float | None = None) -> float | None:
    """Prompt for a float; blank input returns None.

    When `current` is provided it is shown as the editable default and the
    hint changes from "blank to skip" to "blank to clear".
    """
    has_current = current is not None
    hint = "blank to clear" if has_current else "blank to skip"
    raw = typer.prompt(
        f"{label} ({hint})",
        default=str(current) if has_current else "",
        show_default=has_current,
    )
    return float(raw) if raw else None


def _interactive_update_in_place(account: Account, h) -> None:
    """Walk through every field of `h`, mutating it with prompt input."""
    rich.print(
        f"\n[bold cyan]Updating holding[/bold cyan] ([magenta]{h.name}[/magenta])\n"
    )
    h.name = typer.prompt("Name", default=h.name)
    rich.print(f"Current type: [green]{h.type_.value}[/green]")
    if typer.confirm("Change type?", default=False):
        h.type_ = select_asset_type() if account.is_asset else select_liability_type()

    if account.is_asset:
        h.ticker = typer.prompt("Ticker", default=h.ticker)
        h.shares = typer.prompt("Shares", type=float, default=h.shares)
        h.cost_basis = _prompt_optional_float("Cost basis per share", h.cost_basis)
        h.yield_ = _prompt_optional_float("Yield %", h.yield_)
        h.expense_ratio = typer.prompt(
            "Expense ratio", type=float, default=h.expense_ratio
        )
    else:
        h.apr = typer.prompt("APR %", type=float, default=h.apr)
        h.og_principal = typer.prompt(
            "Original principal", type=float, default=h.og_principal
        )
        h.tenure = typer.prompt("Tenure (months)", type=int, default=h.tenure)
