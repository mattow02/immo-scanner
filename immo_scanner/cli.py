import os
import sys

# When frozen by PyInstaller, look for the bundled chromium inside the app
# package instead of the per-user ms-playwright cache (which the exe user does
# not have). Must be set before Playwright is imported or launched.
if getattr(sys, "frozen", False):
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "0")

import logging
import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, FloatPrompt, Confirm
from rich.table import Table
from rich.text import Text

console = Console()

BANNER = r"""[bold cyan]
  ___                            ____
 |_ _|_ __ ___  _ __ ___   ___ / ___|  ___ __ _ _ __  _ __   ___ _ __
  | || '_ ` _ \| '_ ` _ \ / _ \\___ \ / __/ _` | '_ \| '_ \ / _ \\ '__|
  | || | | | | | | | | | | (_) |___) | (_| (_| | | | | | | |  __/ |
 |___|_| |_| |_|_| |_| |_|\___/|____/ \___\__,_|_| |_|_| |_|\___|_|
[/bold cyan]
[dim]Find the best rental investment properties across France.[/dim]
"""

ALL_SITES = {
    "leboncoin": "LeBonCoin (API)",
    "seloger": "SeLoger (HTML)",
    "bienici": "Bien'ici (Browser)",
    "laforet": "Laforet (Browser)",
    "orpi": "Orpi (Browser)",
    "figaro": "Figaro Immo (Browser)",
    "pap": "PAP (Browser)",
}

PROPERTY_TYPES = {
    "apartment": "Apartments",
    "house": "Houses",
    "building": "Entire buildings",
}

MAJOR_CITIES = [
    "Paris", "Lyon", "Marseille", "Toulouse", "Nice",
    "Nantes", "Montpellier", "Strasbourg", "Bordeaux", "Lille",
    "Rennes", "Reims", "Saint-Etienne", "Grenoble", "Dijon",
    "Angers", "Nimes", "Clermont-Ferrand", "Tours", "Rouen",
]


def _header(step: int, total: int, title: str):
    console.print(f"\n[bold blue]Step {step}/{total}[/bold blue] : [bold]{title}[/bold]")
    console.print("[dim]" + "─" * 50 + "[/dim]")


def _interactive_scan():
    console.print(BANNER)
    console.print(Panel("[bold]Interactive mode[/bold] : answer each step to configure your scan.", border_style="blue"))
    total_steps = 6

    # Step 1: Cities
    _header(1, total_steps, "Target cities")
    console.print("[dim]Which cities do you want to scan?[/dim]\n")
    city_table = Table(show_header=False, box=None, padding=(0, 2))
    city_table.add_column(width=4)
    city_table.add_column(width=20)
    city_table.add_column(width=4)
    city_table.add_column(width=20)
    for i in range(0, len(MAJOR_CITIES), 2):
        left = f"[cyan]{i+1:>2}.[/cyan] {MAJOR_CITIES[i]}"
        right = f"[cyan]{i+2:>2}.[/cyan] {MAJOR_CITIES[i+1]}" if i + 1 < len(MAJOR_CITIES) else ""
        city_table.add_row("", left, "", right)
    console.print(city_table)
    console.print(f"\n[cyan] 0.[/cyan] All {len(MAJOR_CITIES)} cities")

    city_input = Prompt.ask(
        "\n[bold]Enter city numbers[/bold] (comma-separated) or city names",
        default="0",
    )

    cities = []
    if city_input.strip() == "0":
        cities = list(MAJOR_CITIES)
    else:
        for part in city_input.split(","):
            part = part.strip()
            try:
                idx = int(part)
                if 1 <= idx <= len(MAJOR_CITIES):
                    cities.append(MAJOR_CITIES[idx - 1])
            except ValueError:
                if part:
                    cities.append(part.capitalize())
    if not cities:
        cities = list(MAJOR_CITIES)

    console.print(f"[green]Selected:[/green] {', '.join(cities)}")

    # Step 2: Budget
    _header(2, total_steps, "Budget range")
    budget_min = IntPrompt.ask("[bold]Minimum price (EUR)[/bold]", default=30000)
    budget_max = IntPrompt.ask("[bold]Maximum price (EUR)[/bold]", default=200000)
    console.print(f"[green]Budget:[/green] {budget_min:,} EUR : {budget_max:,} EUR")

    # Step 3: Property type
    _header(3, total_steps, "Property types")
    for i, (key, label) in enumerate(PROPERTY_TYPES.items(), 1):
        console.print(f"  [cyan]{i}.[/cyan] {label}")
    console.print(f"  [cyan]0.[/cyan] All types")

    type_input = Prompt.ask("[bold]Select types[/bold] (comma-separated)", default="0")
    prop_types = []
    if type_input.strip() == "0":
        prop_types = list(PROPERTY_TYPES.keys())
    else:
        type_keys = list(PROPERTY_TYPES.keys())
        for part in type_input.split(","):
            part = part.strip()
            try:
                idx = int(part)
                if 1 <= idx <= len(type_keys):
                    prop_types.append(type_keys[idx - 1])
            except ValueError:
                if part in PROPERTY_TYPES:
                    prop_types.append(part)
    if not prop_types:
        prop_types = list(PROPERTY_TYPES.keys())

    console.print(f"[green]Types:[/green] {', '.join(PROPERTY_TYPES[t] for t in prop_types)}")

    # Step 4: Sites
    _header(4, total_steps, "Listing sites")
    site_keys = list(ALL_SITES.keys())
    for i, (key, label) in enumerate(ALL_SITES.items(), 1):
        console.print(f"  [cyan]{i}.[/cyan] {label}")
    console.print(f"  [cyan]0.[/cyan] All sites")
    console.print(f"  [cyan]R.[/cyan] Recommended (LeBonCoin + SeLoger) [dim](fastest)[/dim]")

    site_input = Prompt.ask("[bold]Select sites[/bold]", default="R")
    selected_sites = []
    if site_input.strip().upper() == "R":
        selected_sites = ["leboncoin", "seloger"]
    elif site_input.strip() == "0":
        selected_sites = list(site_keys)
    else:
        for part in site_input.split(","):
            part = part.strip()
            try:
                idx = int(part)
                if 1 <= idx <= len(site_keys):
                    selected_sites.append(site_keys[idx - 1])
            except ValueError:
                if part.lower() in ALL_SITES:
                    selected_sites.append(part.lower())
    if not selected_sites:
        selected_sites = ["leboncoin", "seloger"]

    console.print(f"[green]Sites:[/green] {', '.join(ALL_SITES[s] for s in selected_sites)}")

    # Step 5: Yield & options
    _header(5, total_steps, "Yield & options")
    min_yield = FloatPrompt.ask("[bold]Minimum gross yield (%)[/bold]", default=5.0)
    max_pages = IntPrompt.ask("[bold]Pages per site per city[/bold] [dim](1-5)[/dim]", default=2)
    max_pages = max(1, min(5, max_pages))
    no_excel = not Confirm.ask("[bold]Export results to Excel?[/bold]", default=True)

    console.print(f"[green]Min yield:[/green] {min_yield}%  |  [green]Pages:[/green] {max_pages}  |  [green]Excel:[/green] {'No' if no_excel else 'Yes'}")

    # Step 6: Summary & confirm
    _header(6, total_steps, "Summary")
    summary = Table(show_header=False, border_style="blue", box=None, padding=(0, 2))
    summary.add_column(style="bold", width=18)
    summary.add_column()
    summary.add_row("Cities", f"{len(cities)} cities" if len(cities) > 5 else ", ".join(cities))
    summary.add_row("Budget", f"{budget_min:,} : {budget_max:,} EUR")
    summary.add_row("Types", ", ".join(PROPERTY_TYPES[t] for t in prop_types))
    summary.add_row("Sites", ", ".join(selected_sites))
    summary.add_row("Min yield", f"{min_yield}%")
    summary.add_row("Pages/site", str(max_pages))
    summary.add_row("Excel export", "No" if no_excel else "Yes")
    console.print(summary)
    console.print()

    if not Confirm.ask("[bold]Start scan?[/bold]", default=True):
        console.print("[yellow]Scan cancelled.[/yellow]")
        return

    # Run
    from immo_scanner.config import Config
    from immo_scanner.engine import Engine

    config = Config()
    config.budget_min = budget_min
    config.budget_max = budget_max
    config.min_yield = min_yield
    config.sites = selected_sites
    config.max_pages = max_pages
    config.property_types = prop_types

    overrides = {
        "cities": cities,
        "budget_min": budget_min,
        "budget_max": budget_max,
        "property_types": prop_types,
        "max_pages": max_pages,
    }
    criteria = config.to_criteria(**overrides)
    engine = Engine(config)

    console.print("\n[bold blue]═══ Immo-Scanner ═══[/bold blue]\n")
    engine.run(criteria, no_excel=no_excel)


@click.group(invoke_without_command=True)
@click.option("-v", "--verbose", is_flag=True, help="Verbose logging")
@click.pass_context
def main(ctx, verbose):
    """Immo-Scanner : Find the best rental investment properties in France."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    if ctx.invoked_subcommand is None:
        _interactive_scan()


@main.command()
@click.option("--city", multiple=True, help="City to scan (repeatable)")
@click.option("--department", multiple=True, help="Department code (repeatable)")
@click.option("--budget-min", type=int, help="Minimum price (EUR)")
@click.option("--budget-max", type=int, help="Maximum price (EUR)")
@click.option("--surface-min", type=int, help="Minimum area (m2)")
@click.option("--surface-max", type=int, help="Maximum area (m2)")
@click.option("--types", help="Property types (apartment,house,building)")
@click.option("--min-yield", type=float, help="Minimum gross yield (%%)")
@click.option("--sites", help="Sites to scrape (comma-separated)")
@click.option("--max-pages", type=int, help="Max pages per site per city")
@click.option("--rental-mode", type=click.Choice(["avg_price", "cross_ref", "both"]), help="Rent estimation mode")
@click.option("-o", "--output", help="Output directory for Excel")
@click.option("--no-excel", is_flag=True, help="Terminal display only, no Excel export")
def scan(city, department, budget_min, budget_max, surface_min, surface_max,
         types, min_yield, sites, max_pages, rental_mode, output, no_excel):
    """Run a scan with command-line flags (non-interactive)."""
    from immo_scanner.config import Config
    from immo_scanner.engine import Engine

    config = Config()

    overrides = {}
    if city:
        overrides["cities"] = list(city)
    if department:
        overrides["departments"] = list(department)
    if budget_min is not None:
        overrides["budget_min"] = budget_min
        config.budget_min = budget_min
    if budget_max is not None:
        overrides["budget_max"] = budget_max
        config.budget_max = budget_max
    if surface_min is not None:
        overrides["surface_min"] = surface_min
    if surface_max is not None:
        overrides["surface_max"] = surface_max
    if types:
        overrides["property_types"] = [t.strip() for t in types.split(",")]
        config.property_types = overrides["property_types"]
    if min_yield is not None:
        config.min_yield = min_yield
    if sites:
        config.sites = [s.strip() for s in sites.split(",")]
    if max_pages is not None:
        overrides["max_pages"] = max_pages
        config.max_pages = max_pages
    if rental_mode:
        config.rental_mode = rental_mode

    criteria = config.to_criteria(**overrides)
    engine = Engine(config)

    console.print("[bold blue]═══ Immo-Scanner ═══[/bold blue]\n")
    engine.run(criteria, no_excel=no_excel, output=output)


@main.command()
def config():
    """Show active configuration from .env."""
    from immo_scanner.config import Config
    from immo_scanner.display import show_config

    cfg = Config()
    console.print("[bold blue]═══ Configuration ═══[/bold blue]\n")
    show_config(cfg.summary())


@main.command()
def sites():
    """List available scraper sites."""
    table = Table(title="Available Sites", border_style="blue")
    table.add_column("Name", style="cyan")
    table.add_column("Method", style="dim")
    table.add_column("Status", style="green")

    for key, label in ALL_SITES.items():
        table.add_row(key, label, "Active")

    console.print(table)


@main.command()
def doctor():
    """Health check: verify the bundled browser (Playwright/chromium) works."""
    from immo_scanner.utils.browser import BrowserClient, PLAYWRIGHT_AVAILABLE

    console.print("[bold blue]═══ Immo-Scanner doctor ═══[/bold blue]\n")
    if not PLAYWRIGHT_AVAILABLE:
        console.print("[red]FAIL[/red] Playwright is not available in this build.")
        sys.exit(1)
    try:
        with BrowserClient(headless=True, delay_min=0, delay_max=0) as browser:
            page = browser.new_page("about:blank")
            if page is None:
                console.print("[red]FAIL[/red] Could not open a browser page.")
                sys.exit(1)
            page.close()
        console.print("[green]OK[/green] Playwright + chromium launched successfully.")
    except SystemExit:
        raise
    except Exception as exc:
        console.print(f"[red]FAIL[/red] Browser failed to launch: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
