import logging
import click
from rich.console import Console

console = Console()


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Logs détaillés")
def main(verbose):
    """Immo-Scanner — Scanner d'annonces immobilières pour investissement locatif"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )


@main.command()
@click.option("--city", multiple=True, help="Ville(s) à scanner")
@click.option("--department", multiple=True, help="Département(s) à scanner")
@click.option("--budget-min", type=int, help="Budget minimum (€)")
@click.option("--budget-max", type=int, help="Budget maximum (€)")
@click.option("--surface-min", type=int, help="Surface minimum (m²)")
@click.option("--surface-max", type=int, help="Surface maximum (m²)")
@click.option("--types", help="Types de biens (apartment,house,building)")
@click.option("--min-yield", type=float, help="Rendement brut minimum (%%)")
@click.option("--sites", help="Sites à scraper (séparés par des virgules)")
@click.option("--max-pages", type=int, help="Pages max par site")
@click.option("--rental-mode", type=click.Choice(["avg_price", "cross_ref", "both"]), help="Mode estimation loyer")
@click.option("-o", "--output", help="Dossier de sortie pour l'Excel")
@click.option("--no-excel", is_flag=True, help="Pas d'export Excel")
def scan(city, department, budget_min, budget_max, surface_min, surface_max,
         types, min_yield, sites, max_pages, rental_mode, output, no_excel):
    """Lancer un scan des annonces immobilières"""
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

    console.print("[bold blue]═══ Immo-Scanner v1.0 ═══[/bold blue]\n")
    engine.run(criteria, no_excel=no_excel, output=output)


@main.command()
def config():
    """Afficher la configuration active"""
    from immo_scanner.config import Config
    from immo_scanner.display import show_config

    cfg = Config()
    console.print("[bold blue]═══ Configuration ═══[/bold blue]\n")
    show_config(cfg.summary())


@main.command()
def sites():
    """Lister les sites disponibles"""
    from immo_scanner.scrapers import available_scrapers
    from rich.table import Table

    table = Table(title="Sites disponibles", border_style="blue")
    table.add_column("Nom", style="cyan")
    table.add_column("Statut", style="green")

    for name in available_scrapers():
        table.add_row(name, "✓ Actif")

    console.print(table)


if __name__ == "__main__":
    main()
