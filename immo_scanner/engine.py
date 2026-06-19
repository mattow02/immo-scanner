import logging
from immo_scanner.config import Config
from immo_scanner.models import SearchCriteria, Property, ScoredProperty
from immo_scanner.scrapers import get_scraper, available_scrapers
from immo_scanner.dedup import deduplicate
from immo_scanner.scorer import score_properties
from immo_scanner.export import export_excel
from immo_scanner.display import show_results, show_stats, show_config, create_progress, console
from immo_scanner.utils.browser import BrowserClient

logger = logging.getLogger(__name__)


class Engine:
    def __init__(self, config: Config):
        self.config = config

    def run(self, criteria: SearchCriteria, no_excel: bool = False, output: str | None = None) -> list[ScoredProperty]:
        show_config(self.config.summary())

        sites = self.config.sites
        all_properties: list[Property] = []

        console.print(f"[bold]Lancement du navigateur et scan de {len(sites)} sites...[/bold]\n")

        with BrowserClient(headless=True, delay_min=self.config.delay_min, delay_max=self.config.delay_max) as browser:
            with create_progress() as progress:
                task = progress.add_task("Scraping en cours", total=len(sites))

                for site_name in sites:
                    progress.update(task, description=f"[cyan]{site_name}[/cyan]")
                    scraper = get_scraper(site_name, browser=browser)
                    if not scraper:
                        logger.warning(f"Scraper inconnu: {site_name}")
                        progress.advance(task)
                        continue

                    try:
                        props = scraper.search(criteria)
                        all_properties.extend(props)
                        console.print(f"  [green]✓[/green] {site_name}: {len(props)} annonces")
                    except Exception as e:
                        console.print(f"  [red]✗[/red] {site_name}: {e}")
                        logger.error(f"Erreur scraper {site_name}: {e}")

                    progress.advance(task)

        console.print(f"\n[bold]{len(all_properties)} annonces récupérées au total[/bold]")

        console.print("[dim]Déduplication...[/dim]")
        unique = deduplicate(all_properties)
        console.print(f"[bold]{len(unique)} biens uniques après déduplication[/bold]\n")

        console.print("[dim]Calcul des scores et rendements...[/dim]")
        scored = score_properties(unique, self.config.rental_mode)

        filtered = [s for s in scored if s.gross_yield >= self.config.min_yield]
        console.print(f"[bold]{len(filtered)} biens avec rendement >= {self.config.min_yield}%[/bold]\n")

        show_results(scored, min_yield=self.config.min_yield)
        console.print()
        show_stats(scored)

        if not no_excel and filtered:
            output_dir = output or self.config.output_dir
            filepath = export_excel(filtered, output_dir, self.config.excel_name)
            console.print(f"\n[bold green]Excel exporté :[/bold green] {filepath}")

        return scored
