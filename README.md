<div align="center">

**[English](#)** | **[Francais](README.fr.md)**

# Immo-Scanner

**Find the best rental investment properties across France's top real estate platforms.**

Scans 7 major listing sites, estimates rental yield, scores each property, and exports a ranked Excel report.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## Table of Contents

- [Prerequisites](#prerequisites)
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

## Prerequisites

### Install Python (required for all setups except pre-built binary)

<details>
<summary><strong>Windows — Step by step</strong></summary>

1. Go to **https://www.python.org/downloads/**
2. Click the big yellow **"Download Python 3.12.x"** button
3. Run the installer
4. **IMPORTANT: Check the box "Add Python to PATH"** at the bottom of the first screen
5. Click **"Install Now"**
6. When done, open a terminal (press `Win + R`, type `cmd`, press Enter) and verify:
   ```
   python --version
   ```
   You should see `Python 3.12.x`. If you see an error, restart your computer and try again.

</details>

<details>
<summary><strong>Linux (Ubuntu/Debian)</strong></summary>

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip git
python3 --version  # should show 3.12+
```

</details>

<details>
<summary><strong>macOS</strong></summary>

```bash
brew install python@3.12 git
python3 --version
```

</details>

---

## Windows Setup

### Option 1: One-click run (recommended)

1. **Download the project:**
   - Click the green **"Code"** button at the top of this page
   - Click **"Download ZIP"**
   - Extract the ZIP somewhere (e.g. your Desktop)

   Or if you have Git:
   ```
   git clone https://github.com/mattow02/immo-scanner.git
   ```

2. **Open the extracted folder** and **double-click `setup-and-run.bat`**
   - First run: installs everything, opens `.env` in Notepad for you to configure
   - Next runs: launches the interactive scanner directly

3. **Follow the prompts** — pick cities, budget, sites, done.

The Excel report is saved in the `output/` folder.

### Option 2: Build a standalone `.exe`

If you want a portable executable that works without Python:

1. **Double-click `build-windows.bat`**
2. Wait for the build to finish (~2 minutes)
3. Your executable is at `dist\immo-scanner.exe`
4. Copy `immo-scanner.exe` + your `.env` file anywhere and run it

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
curl -LO https://github.com/mattow02/immo-scanner/releases/latest/download/immo-scanner-linux
chmod +x immo-scanner-linux

curl -LO https://raw.githubusercontent.com/mattow02/immo-scanner/main/.env.example
mv .env.example .env
nano .env

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

LeBonCoin and SeLoger work out of the box. For Laforet, Orpi, and Figaro, also run:

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
  - Suspicious price/m2 anomalies
  - Duplicates across sites
```

---

## Usage

### Interactive mode (default)

Run `immo-scanner` with no arguments:

```
Step 1/6 — Target cities
Step 2/6 — Budget range
Step 3/6 — Property types
Step 4/6 — Listing sites
Step 5/6 — Yield & options
Step 6/6 — Summary → Start scan? [Y/n]
```

### Command-line mode

```bash
immo-scanner scan --city Lyon --budget-max 150000 --min-yield 7
immo-scanner scan --city Paris --city Marseille --city Bordeaux
immo-scanner scan --sites leboncoin --city Strasbourg --no-excel
immo-scanner config
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

Copy `.env.example` to `.env` and edit:

```env
IMMO_CITIES=Lyon,Marseille,Bordeaux      # Target cities
IMMO_BUDGET_MIN=30000                     # Min price (EUR)
IMMO_BUDGET_MAX=200000                    # Max price (EUR)
IMMO_SURFACE_MIN=15                       # Min area (m2)
IMMO_TYPES=apartment,house,building       # Property types
IMMO_RENTAL_MODE=both                     # avg_price | cross_ref | both
IMMO_MIN_YIELD=5.0                        # Min gross yield (%)
IMMO_SITES=leboncoin,seloger              # Sites to use
IMMO_MAX_PAGES=3                          # Pages per site per city
IMMO_OUTPUT_DIR=./output                  # Excel output folder
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

---

## Excel Output

The `.xlsx` file has 3 tabs:

| Tab | Content |
|-----|---------|
| **Ranking** | Properties sorted by score with links |
| **Details** | Full data: description, rooms, DPE, GPS, score breakdown |
| **Statistics** | Summary: count, avg/median yield, top cities, sources |

Color coding: green (yield >= 8%), orange (5-8%), red (< 5%).

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

---

## How Anti-Bot Bypass Works

**1. TLS Fingerprinting** (LeBonCoin, SeLoger) — `curl_cffi` impersonates Chrome's TLS handshake signature. DataDome can't tell the difference. No captcha needed.

**2. Headless Browser** (Bien'ici, Laforet, Orpi) — Real Chromium with `playwright-stealth` patches.

---

## Build From Source

**Linux:**
```bash
source venv/bin/activate
pip install pyinstaller
python build.py
# Output: dist/immo-scanner
```

**Windows:** double-click `build-windows.bat`, or:
```powershell
venv\Scripts\activate
pip install pyinstaller
python build.py
# Output: dist\immo-scanner.exe
```

---

## Disclaimer

This tool is for **personal use and educational purposes only**. Scraping may violate the terms of service of some websites. Use responsibly and respect rate limits.

## License

MIT
