from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskID
from rich.panel import Panel
from rich.text import Text
from immo_scanner.models import ScoredProperty

console = Console()


def show_config(config_summary: dict):
    table = Table(title="Configuration active", show_header=False, border_style="blue")
    table.add_column("Paramètre", style="cyan")
    table.add_column("Valeur", style="white")
    for key, val in config_summary.items():
        table.add_row(key, str(val))
    console.print(table)
    console.print()


def show_results(scored: list[ScoredProperty], min_yield: float = 0, limit: int = 50):
    filtered = [s for s in scored if s.gross_yield >= min_yield]
    if not filtered:
        console.print("[yellow]Aucun bien trouvé avec les critères spécifiés.[/yellow]")
        return

    table = Table(
        title=f"Top {min(limit, len(filtered))} biens - Investissement locatif",
        border_style="green",
        show_lines=True,
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("Score", style="bold", width=6)
    table.add_column("Ville", style="cyan", width=15)
    table.add_column("Type", width=10)
    table.add_column("Surface", width=8)
    table.add_column("Prix", style="green", width=12)
    table.add_column("Loyer est.", style="yellow", width=10)
    table.add_column("Rdt brut", width=8)
    table.add_column("Rdt net", width=8)
    table.add_column("Prix/m²", width=10)
    table.add_column("Source", style="dim", width=12)

    for i, sp in enumerate(filtered[:limit], 1):
        p = sp.property

        if sp.score >= 70:
            score_style = "bold green"
        elif sp.score >= 50:
            score_style = "bold yellow"
        else:
            score_style = "bold red"

        if sp.gross_yield >= 8:
            yield_style = "bold green"
        elif sp.gross_yield >= 5:
            yield_style = "yellow"
        else:
            yield_style = "red"

        table.add_row(
            str(i),
            Text(f"{sp.score}", style=score_style),
            p.city[:15] if p.city else "?",
            p.property_type[:10] if p.property_type else "?",
            f"{p.surface:.0f} m²" if p.surface else "?",
            f"{p.price:,} €".replace(",", " "),
            f"{sp.monthly_rent:,.0f} €" if sp.monthly_rent else "?",
            Text(f"{sp.gross_yield:.1f}%", style=yield_style),
            f"{sp.net_yield:.1f}%" if sp.net_yield else "?",
            f"{p.price_per_sqm:,.0f} €" if p.price_per_sqm else "?",
            p.source,
        )

    console.print(table)
    console.print(f"\n[dim]{len(filtered)} biens trouvés au total (affichage limité à {limit})[/dim]")


def show_stats(scored: list[ScoredProperty]):
    if not scored:
        return

    yields = [s.gross_yield for s in scored if s.gross_yield > 0]
    cities: dict[str, int] = {}
    sources: dict[str, int] = {}
    for s in scored:
        city = s.property.city or "Inconnu"
        cities[city] = cities.get(city, 0) + 1
        sources[s.property.source] = sources.get(s.property.source, 0) + 1

    panel_text = []
    panel_text.append(f"Biens analysés : [bold]{len(scored)}[/bold]")
    if yields:
        avg_yield = sum(yields) / len(yields)
        sorted_yields = sorted(yields)
        median_yield = sorted_yields[len(sorted_yields) // 2]
        panel_text.append(f"Rendement moyen : [bold]{avg_yield:.1f}%[/bold]")
        panel_text.append(f"Rendement médian : [bold]{median_yield:.1f}%[/bold]")
        panel_text.append(f"Meilleur rendement : [bold green]{max(yields):.1f}%[/bold green]")

    panel_text.append(f"\nTop villes :")
    for city, count in sorted(cities.items(), key=lambda x: -x[1])[:5]:
        panel_text.append(f"  {city}: {count} biens")

    panel_text.append(f"\nPar source :")
    for source, count in sorted(sources.items(), key=lambda x: -x[1]):
        panel_text.append(f"  {source}: {count}")

    console.print(Panel("\n".join(panel_text), title="Statistiques", border_style="blue"))


def create_progress() -> Progress:
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("({task.completed}/{task.total})"),
        console=console,
    )
