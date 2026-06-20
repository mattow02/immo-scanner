<div align="center">

# Immo-Scanner

**Find the best rental investment properties across France's top real estate platforms.**

Scans 7 major listing sites, estimates rental yield, scores each property, and exports a ranked Excel report.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## Table of Contents

- [Windows Setup](#windows-setup)
- [Linux Setup](#linux-setup)
- [How It Works](#how-it-works)
- [Usage](#usage)
- [Configuration](#configuration)
- [Scoring System](#scoring-system)
- [Excel Output](#excel-output)
- [Supported Sites](#supported-sites)
- [Anti-Bot Bypass](#how-anti-bot-bypass-works)
- [Build From Source](#build-from-source)

---

## Windows Setup

### Option 1: One-click run (recommended)

> Requires [Python 3.12+](https://www.python.org/downloads/) installed with **"Add Python to PATH"** checked.

1. **Download or clone** the project:
   ```
   git clone https://github.com/mattow02/immo-scanner.git
   ```
   Or download as ZIP from the green **Code** button above, and extract it.

2. **Double-click `setup-and-run.bat`** in the project folder.
   - First run: installs everything automatically, opens `.env` in Notepad for you to configure
   - Next runs: launches the interactive scanner directly

3. **Follow the prompts** — pick your cities, budget, sites, and go.

That's it. The Excel report will be saved in the `output/` folder.

### Option 2: Build a standalone `.exe`

If you want a single executable that works without Python:

1. Install [Python 3.12+](https://www.python.org/downloads/) (check **"Add Python to PATH"**)
2. **Double-click `build-windows.bat`**
3. Your executable is at `dist\immo-scanner.exe`
4. Copy `immo-scanner.exe` + `.env` wherever you want and run it:
   ```
   immo-scanner.exe
   ```

### Option 3: Manual install (PowerShell / CMD)

```powershell
git clone https://github.com/mattow02/immo-scanner.git
cd immo-scanner

python -m venv venv
venv\Scripts\activate

pip install -e .

copy .env.example .env
notepad .env

immo-scanner
```

### Windows troubleshooting

| Problem | Fix |
|---------|-----|
| `python is not recognized` | Reinstall Python, check **"Add Python to PATH"** |
| `pip is not recognized` | Run `python -m pip install -e .` instead |
| Red text / encoding errors | Run `chcp 65001` before launching (enables UTF-8) |
| Excel won't open | Check the `output/` folder, file is named `resultats_immo_YYYYMMDD_HHMMSS.xlsx` |
| `curl_cffi` install fails | Install [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) |

---

## Linux Setup

### Option 1: Pre-built binary

```bash
# Download from releases
curl -LO https://github.com/mattow02/immo-scanner/releases/latest/download/immo-scanner-linux
chmod +x immo-scanner-linux

# Create config
curl -LO https://raw.githubusercontent.com/mattow02/immo-scanner/main/.env.example
mv .env.example .env
nano .env  # edit your preferences

# Run
./immo-scanner-linux
```

### Option 2: Install from source

```bash
git clone https://github.com/mattow02/immo-scanner.git
cd immo-scanner

python3 -m venv venv
source venv/bin/activate

pip install -e .

cp .env.example .env
nano .env

immo-scanner
```

### Optional: enable browser-based scrapers

LeBonCoin and SeLoger work out of the box. For Laforet, Orpi, and Figaro (browser-based), also run:

```bash
pip install playwright playwright-stealth
playwright install chromium
```

---

## How It Works

```
 You run immo-scanner
        |
        v
 +-----------------+     +-----------------+     +------------------+
 | Scrape listings |---->| Score & rank    |---->| Export Excel      |
 | from 7 sites    |     | by yield, price |     | 3 tabs, links,   |
 | (API + browser) |     | demand, type... |     | colors, stats    |
 +-----------------+     +-----------------+     +------------------+
        |
  Filters out:
  - Viager (life annuities)
  - Managed residences / EHPAD
  - Caves, parkings, garages
  - Suspicious price/m² anomalies
  - Duplicates across sites
```

---

## Usage

### Interactive mode (default)

Just run `immo-scanner` with no arguments. A step-by-step wizard guides you through:

```
Step 1/6 — Target cities
Step 2/6 — Budget range
Step 3/6 — Property types
Step 4/6 — Listing sites
Step 5/6 — Yield & options
Step 6/6 — Summary → Start scan? [Y/n]
```

### Command-line mode

For scripting or quick runs, use flags directly:

```bash
# Single city
immo-scanner scan --city Lyon --budget-max 150000 --min-yield 7

# Multiple cities
immo-scanner scan --city Paris --city Marseille --city Bordeaux

# Specific site, no Excel
immo-scanner scan --sites leboncoin --city Strasbourg --max-pages 3 --no-excel

# Show config
immo-scanner config

# List available sites
immo-scanner sites
```

### All flags

| Flag | Description | Example |
|------|-------------|---------|
| `--city` | City to scan (repeatable) | `--city Lyon --city Paris` |
| `--department` | Department code (repeatable) | `--department 69` |
| `--budget-min` | Minimum price (EUR) | `--budget-min 50000` |
| `--budget-max` | Maximum price (EUR) | `--budget-max 150000` |
| `--surface-min` | Minimum area (m2) | `--surface-min 20` |
| `--surface-max` | Maximum area (m2) | `--surface-max 80` |
| `--types` | Property types | `--types apartment,house` |
| `--min-yield` | Minimum gross yield (%) | `--min-yield 6` |
| `--sites` | Sites to scrape | `--sites leboncoin,seloger` |
| `--max-pages` | Max pages per site per city | `--max-pages 3` |
| `--rental-mode` | Rent estimation mode | `--rental-mode avg_price` |
| `-o, --output` | Output directory for Excel | `-o ./results` |
| `--no-excel` | Terminal display only | `--no-excel` |
| `-v, --verbose` | Verbose logging | |

---

## Configuration

All settings live in a `.env` file. Copy `.env.example` to `.env` and edit:

```env
# === SEARCH ===
IMMO_CITIES=Lyon,Marseille,Bordeaux      # Target cities
IMMO_BUDGET_MIN=30000                     # Min price (EUR)
IMMO_BUDGET_MAX=200000                    # Max price (EUR)
IMMO_SURFACE_MIN=15                       # Min area (m2)
IMMO_TYPES=apartment,house,building       # Property types

# === YIELD ===
IMMO_RENTAL_MODE=both                     # avg_price | cross_ref | both
IMMO_MIN_YIELD=5.0                        # Min gross yield (%)

# === SCRAPING ===
IMMO_SITES=leboncoin,seloger              # Sites to use
IMMO_MAX_PAGES=3                          # Pages per site per city
IMMO_DELAY_MIN=2                          # Min delay between requests (sec)
IMMO_DELAY_MAX=5                          # Max delay between requests (sec)

# === OUTPUT ===
IMMO_OUTPUT_DIR=./output                  # Excel output folder
IMMO_EXCEL_NAME=resultats_immo            # Excel filename prefix
```

### Rental estimation modes

| Mode | Speed | Accuracy | Description |
|------|-------|----------|-------------|
| `avg_price` | Fast | Medium | Built-in rent/m2 database for 50+ French cities |
| `cross_ref` | Slow | High | Scrapes actual rental listings to estimate real market rent |
| `both` | Medium | Best | Combines both methods **(default)** |

---

## Scoring System

Each property gets a score from 0 to 100:

| Criterion | Weight | What it measures |
|-----------|--------|------------------|
| **Gross yield** | 40% | `(monthly rent x 12) / price x 100` |
| **Price/m2 vs city avg** | 15% | Below average = good deal |
| **Rental demand** | 15% | Local supply/demand tension |
| **Property type** | 10% | Studios & T2 score higher (easier to rent) |
| **Size coherence** | 10% | Area must match room count |
| **Listing freshness** | 10% | Recent listings score higher |

### Yield formulas

```
Gross yield = (monthly rent x 12) / purchase price x 100

Net yield   = (annual rent - tax - fees - 1 month vacancy) / purchase price x 100
```

---

## Excel Output

The `.xlsx` file has 3 tabs:

| Tab | Content |
|-----|---------|
| **Ranking** | Properties sorted by score. Columns: rank, score, city, type, area, price, rent, yield, price/m2, link |
| **Details** | All data: description, rooms, floor, DPE, charges, GPS coords, score breakdown |
| **Statistics** | Summary: total count, avg/median yield, top cities, source breakdown |

Color coding: green (yield >= 8%), orange (5-8%), red (< 5%). All listing links are clickable.

---

## Auto-Filtering

These listings are automatically excluded:

| Category | Keywords detected |
|----------|-------------------|
| Life annuities | viager, bouquet, rente viagere, occupe a vie |
| Managed residences | residence senior, geree, etudiante, services |
| Healthcare | EHPAD |
| Commercial | bail commercial, local commercial, murs commerciaux |
| Non-housing | caves a vendre, parking a vendre, box, garage a vendre |
| Price anomalies | Price/m2 below 30% of city average |

---

## Supported Sites

| Site | Method | Needs Playwright? | Status |
|------|--------|-------------------|--------|
| **LeBonCoin** | JSON API + TLS impersonation | No | Fully working |
| **SeLoger** | HTML + TLS impersonation | No | Fully working |
| **Bien'ici** | Browser rendering | Yes | Working |
| **Laforet** | Browser rendering | Yes | Working |
| **Orpi** | Browser rendering | Yes | Working |
| **Figaro Immo** | Browser rendering | Yes | Working |
| **PAP** | Browser rendering | Yes | Partial |

> LeBonCoin and SeLoger work everywhere (standalone exe, Windows, Linux). The browser-based sites require Playwright to be installed separately.

---

## How Anti-Bot Bypass Works

French real estate sites use **DataDome** bot protection. This tool bypasses it with two methods:

**1. TLS Fingerprinting** (LeBonCoin, SeLoger)

DataDome checks the TLS handshake signature (JA3/JA4 hash). Normal Python HTTP libraries have a different fingerprint than real browsers and get blocked. `curl_cffi` impersonates Chrome's exact TLS fingerprint, making requests look identical to a real browser. No captcha needed.

**2. Headless Browser** (Bien'ici, Laforet, Orpi)

A real Chromium browser runs in headless mode with `playwright-stealth` patches that hide automation signals (`navigator.webdriver`, WebGL fingerprint, etc).

---

## Build From Source

### Build the executable yourself

**Linux:**
```bash
source venv/bin/activate
pip install pyinstaller
python build.py
# Output: dist/immo-scanner
```

**Windows:**
```
Double-click build-windows.bat
```
Or manually:
```powershell
venv\Scripts\activate
pip install pyinstaller
python build.py
# Output: dist\immo-scanner.exe
```

### Project structure

```
immo-scanner/
├── immo_scanner/
│   ├── cli.py              # CLI + interactive wizard
│   ├── config.py            # .env loader
│   ├── models.py            # Data models
│   ├── engine.py            # Main orchestrator
│   ├── scorer.py            # Yield + scoring + anomaly filter
│   ├── dedup.py             # Cross-site deduplication
│   ├── display.py           # Terminal output (Rich)
│   ├── export.py            # Excel export (openpyxl)
│   ├── scrapers/            # One file per site
│   └── utils/               # HTTP, browser, geo data, rent data
├── build.py                 # PyInstaller build script
├── build-windows.bat        # Windows build (double-click)
├── setup-and-run.bat        # Windows quick start (double-click)
├── .env.example             # Config template
└── README.md
```

---

## Disclaimer

This tool is for **personal use and educational purposes only**. Scraping may violate the terms of service of some websites. Use responsibly, respect rate limits, and do not use for commercial purposes without authorization.

## License

MIT
