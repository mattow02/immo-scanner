import logging
from immo_scanner.config import Config
from immo_scanner.models import SearchCriteria, Property, ScoredProperty
from immo_scanner.scrapers import get_scraper, available_scrapers
from immo_scanner.dedup import deduplicate
from immo_scanner.scorer import score_properties
from immo_scanner.export import export_excel
from immo_scanner.display import show_results, show_stats, show_config, create_progress, console
from immo_scanner.utils.browser import PLAYWRIGHT_AVAILABLE

logger = logging.getLogger(__name__)

BROWSER_SITES = {"laforet", "orpi", "figaro", "bienici"}


class Engine:
    def __init__(self, config: Config):
        self.config = config

    def run(self, criteria: SearchCriteria, no_excel: bool = False, output: str | None = None) -> list[ScoredProperty]:
        show_config(self.config.summary())

        sites = self.config.sites
        needs_browser = any(s in BROWSER_SITES for s in sites)
        all_properties: list[Property] = []

        browser = None
        browser_ctx = None
        if needs_browser and PLAYWRIGHT_AVAILABLE:
            from immo_scanner.utils.browser import BrowserClient
            browser_ctx = BrowserClient(headless=True, delay_min=self.config.delay_min, delay_max=self.config.delay_max)
            browser = browser_ctx.start()

        try:
            console.print(f"[bold]Scanning {len(sites)} sites...[/bold]\n")

            with create_progress() as progress:
                task = progress.add_task("Scraping", total=len(sites))

                for site_name in sites:
                    progress.update(task, description=f"[cyan]{site_name}[/cyan]")

                    if site_name in BROWSER_SITES and not PLAYWRIGHT_AVAILABLE:
                        console.print(f"  [yellow]⊘[/yellow] {site_name}: [dim]skipped (Playwright not installed)[/dim]")
                        progress.advance(task)
                        continue

                    scraper = get_scraper(site_name, browser=browser)
                    if not scraper:
                        logger.warning(f"Unknown scraper: {site_name}")
                        progress.advance(task)
                        continue

                    try:
                        props = scraper.search(criteria)
                        all_properties.extend(props)
                        console.print(f"  [green]✓[/green] {site_name}: {len(props)} listings")
                    except Exception as e:
                        console.print(f"  [red]✗[/red] {site_name}: {e}")
                        logger.error(f"Scraper error {site_name}: {e}")

                    progress.advance(task)
        finally:
            if browser_ctx:
                browser_ctx.stop()

        console.print(f"\n[bold]{len(all_properties)} listings fetched[/bold]")

        console.print("[dim]Deduplicating...[/dim]")
        unique = deduplicate(all_properties)
        console.print(f"[bold]{len(unique)} unique properties[/bold]\n")

        console.print("[dim]Scoring & yield calculation...[/dim]")
        scored = score_properties(unique, self.config.rental_mode)

        filtered = [s for s in scored if s.gross_yield >= self.config.min_yield]
        console.print(f"[bold]{len(filtered)} properties with yield >= {self.config.min_yield}%[/bold]\n")

        show_results(scored, min_yield=self.config.min_yield)
        console.print()
        show_stats(scored)

        if not no_excel and filtered:
            output_dir = output or self.config.output_dir
            filepath = export_excel(filtered, output_dir, self.config.excel_name)
            console.print(f"\n[bold green]Excel exported:[/bold green] {filepath}")

        return scored
