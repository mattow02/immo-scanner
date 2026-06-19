<div align="center">

# Immo-Scanner

**Find the best rental investment properties across France's top real estate platforms.**

Scans 7 major listing sites, estimates rental yield, scores each property, and exports a ranked Excel report.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## Features

- **7 listing sites** — LeBonCoin, SeLoger, Bien'ici, Laforet, Orpi, Figaro Immo, PAP
- **Anti-bot bypass** — TLS fingerprint impersonation via `curl_cffi` (LeBonCoin, SeLoger) + Playwright stealth for JS-heavy sites
- **Smart scoring** — Multi-criteria scoring (0–100) based on gross yield, price/m² vs. city average, rental demand, property type, and listing freshness
- **Dual rent estimation** — Built-in average rent database (50+ cities) or cross-reference with actual rental listings
- **Auto-filtering** — Excludes life annuities (viager), managed residences, EHPAD, commercial leases
- **Cross-site deduplication** — Same property listed on multiple sites? Kept once, with the most complete data
- **Excel export** — 3-tab `.xlsx` with conditional formatting, clickable links, and statistics
- **CLI with overrides** — Configure defaults in `.env`, override anything per-run via flags

## Supported Sites

| Site | Method | Status |
|------|--------|--------|
| **LeBonCoin** | JSON API + `curl_cffi` | Fully working |
| **SeLoger** | HTML scraping + `curl_cffi` | Fully working |
| **Bien'ici** | Playwright (JS rendering) | Working |
| **Laforet** | Playwright (JS rendering) | Working |
| **Orpi** | Playwright (JS rendering) | Working |
| **Figaro Immo** | Playwright (JS rendering) | Working |
| **PAP** | Playwright (JS rendering) | Partial |

## Quick Start

### 1. Install

```bash
git clone https://github.com/mattow02/immo-scanner.git
cd immo-scanner

python3 -m venv venv
source venv/bin/activate

pip install -e .
playwright install chromium
```

### 2. Configure

```bash
cp .env.example .env
```

Edit `.env` to set your target cities, budget, and preferences:

```env
IMMO_CITIES=Lyon,Bordeaux,Toulouse
IMMO_BUDGET_MIN=30000
IMMO_BUDGET_MAX=200000
IMMO_MIN_YIELD=5.0
IMMO_SITES=leboncoin,seloger,bienici
```

### 3. Scan

```bash
# Use .env defaults
immo-scanner scan

# Override on the fly
immo-scanner scan --city Strasbourg --budget-max 100000 --min-yield 7

# Multiple cities
immo-scanner scan --city Lyon --city Marseille --city Bordeaux

# Specific site only
immo-scanner scan --sites leboncoin --city Paris --max-pages 3
```

## Usage

### Commands

```bash
immo-scanner scan       # Run a full scan
immo-scanner config     # Show active configuration
immo-scanner sites      # List available scraper sites
```

### Scan Options

| Flag | Description | Example |
|------|-------------|---------|
| `--city` | City to scan (repeatable) | `--city Lyon --city Paris` |
| `--department` | Department code (repeatable) | `--department 69` |
| `--budget-min` | Minimum price (EUR) | `--budget-min 50000` |
| `--budget-max` | Maximum price (EUR) | `--budget-max 150000` |
| `--surface-min` | Minimum area (m²) | `--surface-min 20` |
| `--surface-max` | Maximum area (m²) | `--surface-max 80` |
| `--types` | Property types (comma-separated) | `--types apartment,house` |
| `--min-yield` | Minimum gross yield (%) | `--min-yield 6` |
| `--sites` | Sites to scrape (comma-separated) | `--sites leboncoin,seloger` |
| `--max-pages` | Max pages per site per city | `--max-pages 3` |
| `--rental-mode` | Rent estimation mode | `--rental-mode avg_price` |
| `-o, --output` | Output directory for Excel | `-o ./results` |
| `--no-excel` | Terminal display only | `--no-excel` |
| `-v, --verbose` | Verbose logging | |

### Rental Estimation Modes

| Mode | Description |
|------|-------------|
| `avg_price` | Uses built-in rent/m² averages for 50+ French cities. Fast, no extra requests. |
| `cross_ref` | Scrapes rental listings on the same sites to estimate real market rent. Slower but more accurate. |
| `both` | Uses `avg_price` as baseline, enriched with `cross_ref` data when available. **(default)** |

## Scoring System

Each property receives a score from 0 to 100 based on weighted criteria:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Gross yield** | 40% | `(annual rent / purchase price) × 100` — higher is better |
| **Price/m² vs. city avg** | 15% | Below-average price per m² = good deal |
| **Rental demand** | 15% | Local supply/demand tension index |
| **Property type** | 10% | Studios & 2-room flats score higher (easier to rent) |
| **Size coherence** | 10% | Area must match room count (no 50m² studio) |
| **Listing freshness** | 10% | Recent listings score higher |

### Yield Calculation

```
Gross yield  = (estimated monthly rent × 12) / purchase price × 100

Net yield    = ((annual rent) - (property tax + condo fees + 1 month vacancy)) / purchase price × 100
```

## Excel Output

The generated `.xlsx` file contains 3 tabs:

### Ranking
Sorted by score. Columns: rank, score, city, type, area, price, estimated rent, gross yield, net yield, price/m², link, source.

### Details
All columns above plus: description, rooms, floor, year built, energy rating (DPE), charges, coordinates, posting date, score breakdown.

### Statistics
Summary: total properties, average/median yield, best yield, top cities, breakdown by source.

Conditional formatting: green (yield ≥ 8%), orange (5–8%), red (< 5%). Links are clickable.

## Auto-Filtering

The following listing types are automatically excluded:

- **Life annuities** — viager, bouquet, rente viagère, occupé à vie
- **Managed residences** — résidence senior, résidence gérée, résidence étudiante, résidence de services
- **Healthcare** — EHPAD
- **Managed LMNP** — LMNP géré
- **Commercial** — bail commercial, droit au bail, murs commerciaux

## Configuration Reference

All settings can be defined in `.env` (see [`.env.example`](.env.example)):

```env
# Search zone
IMMO_CITIES=Lyon,Marseille,Bordeaux      # Target cities
IMMO_DEPARTMENTS=                         # Or by department code (69,13,33)
IMMO_RADIUS_KM=20                         # Radius around each city

# Filters
IMMO_BUDGET_MIN=30000                     # Min purchase price
IMMO_BUDGET_MAX=200000                    # Max purchase price
IMMO_SURFACE_MIN=15                       # Min area (m²)
IMMO_SURFACE_MAX=                         # Max area (empty = no limit)
IMMO_TYPES=apartment,house,building       # Property types
IMMO_ROOMS_MIN=                           # Min rooms
IMMO_ROOMS_MAX=                           # Max rooms

# Rental estimation
IMMO_RENTAL_MODE=both                     # avg_price | cross_ref | both
IMMO_MIN_YIELD=5.0                        # Min gross yield to appear in results

# Scraping
IMMO_SITES=leboncoin,seloger,bienici      # Sites to scrape
IMMO_MAX_PAGES=3                          # Pages per site per city
IMMO_DELAY_MIN=2                          # Min delay between requests (sec)
IMMO_DELAY_MAX=5                          # Max delay between requests (sec)
IMMO_TIMEOUT=15                           # Request timeout (sec)

# Export
IMMO_OUTPUT_DIR=./output                  # Output folder
IMMO_EXCEL_NAME=resultats_immo            # Excel filename (without .xlsx)
```

## Project Structure

```
immo-scanner/
├── immo_scanner/
│   ├── cli.py              # CLI entry point (Click)
│   ├── config.py            # .env loader
│   ├── models.py            # Data models (Property, ScoredProperty)
│   ├── engine.py            # Main orchestrator
│   ├── scorer.py            # Yield calculation & multi-criteria scoring
│   ├── dedup.py             # Cross-site deduplication
│   ├── display.py           # Rich terminal output
│   ├── export.py            # Excel generation (openpyxl)
│   ├── scrapers/
│   │   ├── base.py          # Abstract scraper + auto-filtering
│   │   ├── leboncoin.py     # LeBonCoin (API + curl_cffi)
│   │   ├── seloger.py       # SeLoger (HTML + curl_cffi)
│   │   ├── bienici.py       # Bien'ici (Playwright)
│   │   ├── laforet.py       # Laforet (Playwright)
│   │   ├── orpi.py          # Orpi (Playwright)
│   │   ├── figaro.py        # Figaro Immo (Playwright)
│   │   └── pap.py           # PAP (Playwright)
│   └── utils/
│       ├── browser.py       # Playwright + stealth wrapper
│       ├── http.py          # HTTP client (retry, rate limit)
│       ├── geo.py           # City/postal code mapping
│       └── rental_refs.py   # Rent averages & rental demand data
├── .env.example
├── requirements.txt
├── setup.py
└── README.md
```

## How Anti-Bot Bypass Works

Most French real estate sites use **DataDome** or **Cloudflare** bot protection. This tool uses two strategies:

1. **TLS Fingerprinting** (`curl_cffi`) — LeBonCoin and SeLoger detect bots by comparing the TLS handshake signature (JA3/JA4 hash) against known browser fingerprints. `curl_cffi` impersonates Chrome's exact TLS fingerprint, making requests indistinguishable from a real browser. No captcha solving needed.

2. **Headless Browser** (`Playwright + stealth`) — For JS-rendered sites (Bien'ici, Laforet, Orpi), a headless Chromium browser with stealth patches renders the page like a real user.

## Disclaimer

This tool is for **personal use and educational purposes only**. Scraping may violate the terms of service of some websites. Use responsibly, respect rate limits, and do not use for commercial purposes without authorization. The authors are not responsible for any misuse.

## License

MIT
