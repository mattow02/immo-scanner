<div align="center">

**[English](README.md)** | **[Francais](#)**

# Immo-Scanner

**Trouvez les meilleurs biens immobiliers pour investissement locatif en France.**

Scanne 7 sites d'annonces, estime le rendement locatif, note chaque bien, et exporte un rapport Excel classe.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## Sommaire

- [Installer Python](#installer-python)
- [Installation Windows](#installation-windows)
- [Installation Linux](#installation-linux)
- [Comment ca marche](#comment-ca-marche)
- [Utilisation](#utilisation)
- [Configuration](#configuration)
- [Systeme de scoring](#systeme-de-scoring)
- [Fichier Excel](#fichier-excel)
- [Sites supportes](#sites-supportes)
- [Contournement anti-bot](#contournement-anti-bot)
- [Compiler depuis les sources](#compiler-depuis-les-sources)

---

## Installer Python

> Python est necessaire pour toutes les installations sauf le binaire pre-compile Linux.

<details>
<summary><strong>Windows — Etape par etape</strong></summary>

1. Allez sur **https://www.python.org/downloads/**
2. Cliquez sur le gros bouton jaune **"Download Python 3.12.x"**
3. Lancez l'installateur telecharge
4. **IMPORTANT : Cochez la case "Add Python to PATH"** en bas du premier ecran
5. Cliquez sur **"Install Now"**
6. Une fois termine, ouvrez un terminal (appuyez sur `Win + R`, tapez `cmd`, appuyez sur Entree) et verifiez :
   ```
   python --version
   ```
   Vous devriez voir `Python 3.12.x`. Si erreur, redemarrez votre PC et reessayez.

</details>

<details>
<summary><strong>Linux (Ubuntu/Debian)</strong></summary>

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip git
python3 --version  # doit afficher 3.12+
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

## Installation Windows

### Option 1 : Lancement en un clic (recommande)

1. **Telechargez le projet :**
   - Cliquez sur le bouton vert **"Code"** en haut de cette page
   - Cliquez sur **"Download ZIP"**
   - Extrayez le ZIP quelque part (ex: votre Bureau)

   Ou si vous avez Git :
   ```
   git clone https://github.com/mattow02/immo-scanner.git
   ```

2. **Ouvrez le dossier extrait** et **double-cliquez sur `setup-and-run.bat`**
   - Premier lancement : installe tout automatiquement, ouvre `.env` dans le Bloc-notes pour configurer
   - Lancements suivants : lance directement le scanner interactif

3. **Suivez les etapes** — choisissez vos villes, budget, sites, c'est parti.

Le rapport Excel est sauvegarde dans le dossier `output/`.

### Option 2 : Compiler un `.exe` portable

Si vous voulez un executable qui marche sans Python :

1. **Double-cliquez sur `build-windows.bat`**
2. Attendez la fin du build (~2 minutes)
3. Votre executable est dans `dist\immo-scanner.exe`
4. Copiez `immo-scanner.exe` + votre fichier `.env` ou vous voulez et lancez-le

### Option 3 : Installation manuelle (PowerShell / CMD)

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

### Problemes courants Windows

| Probleme | Solution |
|----------|----------|
| `python is not recognized` | Reinstallez Python en cochant **"Add Python to PATH"** |
| `pip is not recognized` | Lancez `python -m pip install -e .` a la place |
| Caracteres bizarres / texte rouge | Lancez `chcp 65001` avant (active UTF-8) |
| L'Excel ne s'ouvre pas | Verifiez le dossier `output/`, fichier nomme `resultats_immo_YYYYMMDD_HHMMSS.xlsx` |
| Erreur install `curl_cffi` | Installez [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) |

---

## Installation Linux

### Option 1 : Binaire pre-compile

```bash
curl -LO https://github.com/mattow02/immo-scanner/releases/latest/download/immo-scanner-linux
chmod +x immo-scanner-linux

curl -LO https://raw.githubusercontent.com/mattow02/immo-scanner/main/.env.example
mv .env.example .env
nano .env

./immo-scanner-linux
```

### Option 2 : Installation depuis les sources

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

### Optionnel : activer les scrapers navigateur

LeBonCoin et SeLoger marchent directement. Pour Laforet, Orpi et Figaro, lancez aussi :

```bash
pip install playwright playwright-stealth
playwright install chromium
```

---

## Comment ca marche

```
 Vous lancez immo-scanner
        |
        v
 +-----------------+     +-----------------+     +------------------+
 | Scrape les      |---->| Note et classe  |---->| Exporte en Excel |
 | annonces sur    |     | par rendement,  |     | 3 onglets, liens |
 | 7 sites         |     | prix, demande...|     | couleurs, stats  |
 +-----------------+     +-----------------+     +------------------+
        |
  Filtre automatiquement :
  - Viagers (rente viagere, bouquet)
  - Residences gerees / seniors / EHPAD
  - Caves, parkings, garages
  - Prix/m2 anormalement bas
  - Doublons entre sites
```

---

## Utilisation

### Mode interactif (par defaut)

Lancez `immo-scanner` sans arguments :

```
Etape 1/6 — Villes cibles
Etape 2/6 — Fourchette de budget
Etape 3/6 — Types de biens
Etape 4/6 — Sites d'annonces
Etape 5/6 — Rendement et options
Etape 6/6 — Resume → Lancer le scan ? [O/n]
```

### Mode ligne de commande

```bash
immo-scanner scan --city Lyon --budget-max 150000 --min-yield 7
immo-scanner scan --city Paris --city Marseille --city Bordeaux
immo-scanner scan --sites leboncoin --city Strasbourg --no-excel
immo-scanner config
immo-scanner sites
```

### Toutes les options

| Option | Description | Exemple |
|--------|-------------|---------|
| `--city` | Ville a scanner (repetable) | `--city Lyon --city Paris` |
| `--department` | Code departement (repetable) | `--department 69` |
| `--budget-min` | Prix minimum (EUR) | `--budget-min 50000` |
| `--budget-max` | Prix maximum (EUR) | `--budget-max 150000` |
| `--surface-min` | Surface minimum (m2) | `--surface-min 20` |
| `--surface-max` | Surface maximum (m2) | `--surface-max 80` |
| `--types` | Types de biens | `--types apartment,house` |
| `--min-yield` | Rendement brut minimum (%) | `--min-yield 6` |
| `--sites` | Sites a scraper | `--sites leboncoin,seloger` |
| `--max-pages` | Pages max par site par ville | `--max-pages 3` |
| `--rental-mode` | Mode d'estimation du loyer | `--rental-mode avg_price` |
| `-o, --output` | Dossier de sortie Excel | `-o ./resultats` |
| `--no-excel` | Affichage terminal uniquement | `--no-excel` |
| `-v, --verbose` | Logs detailles | |

---

## Configuration

Copiez `.env.example` en `.env` et editez :

```env
IMMO_CITIES=Lyon,Marseille,Bordeaux      # Villes cibles
IMMO_BUDGET_MIN=30000                     # Prix minimum (EUR)
IMMO_BUDGET_MAX=200000                    # Prix maximum (EUR)
IMMO_SURFACE_MIN=15                       # Surface minimum (m2)
IMMO_TYPES=apartment,house,building       # Types de biens
IMMO_RENTAL_MODE=both                     # avg_price | cross_ref | both
IMMO_MIN_YIELD=5.0                        # Rendement brut minimum (%)
IMMO_SITES=leboncoin,seloger              # Sites a utiliser
IMMO_MAX_PAGES=3                          # Pages par site par ville
IMMO_OUTPUT_DIR=./output                  # Dossier de sortie Excel
```

### Modes d'estimation du loyer

| Mode | Vitesse | Precision | Description |
|------|---------|-----------|-------------|
| `avg_price` | Rapide | Moyenne | Base integree de loyers/m2 pour 50+ villes francaises |
| `cross_ref` | Lent | Haute | Scrape les annonces de location pour estimer le loyer reel |
| `both` | Moyen | Meilleure | Combine les deux methodes **(par defaut)** |

---

## Systeme de scoring

Chaque bien recoit une note de 0 a 100 :

| Critere | Poids | Ce qu'il mesure |
|---------|-------|-----------------|
| **Rendement brut** | 40% | `(loyer mensuel x 12) / prix d'achat x 100` |
| **Prix/m2 vs moyenne ville** | 15% | En dessous de la moyenne = bonne affaire |
| **Tension locative** | 15% | Ratio offre/demande locale |
| **Type de bien** | 10% | Studios et T2 mieux notes (plus faciles a louer) |
| **Coherence surface** | 10% | La surface doit correspondre au nombre de pieces |
| **Fraicheur annonce** | 10% | Annonces recentes mieux notees |

---

## Fichier Excel

Le fichier `.xlsx` genere contient 3 onglets :

| Onglet | Contenu |
|--------|---------|
| **Classement** | Biens tries par score avec liens cliquables |
| **Details** | Donnees completes : description, pieces, DPE, GPS, detail du score |
| **Statistiques** | Resume : total, rendement moyen/median, top villes, sources |

Code couleur : vert (rendement >= 8%), orange (5-8%), rouge (< 5%).

---

## Sites supportes

| Site | Methode | Besoin de Playwright ? | Statut |
|------|---------|------------------------|--------|
| **LeBonCoin** | API JSON + empreinte TLS | Non | Fonctionnel |
| **SeLoger** | HTML + empreinte TLS | Non | Fonctionnel |
| **Bien'ici** | Rendu navigateur | Oui | Fonctionnel |
| **Laforet** | Rendu navigateur | Oui | Fonctionnel |
| **Orpi** | Rendu navigateur | Oui | Fonctionnel |
| **Figaro Immo** | Rendu navigateur | Oui | Fonctionnel |
| **PAP** | Rendu navigateur | Oui | Partiel |

---

## Contournement anti-bot

**1. Empreinte TLS** (LeBonCoin, SeLoger) — `curl_cffi` imite l'empreinte TLS exacte de Chrome. DataDome ne fait pas la difference. Pas de captcha.

**2. Navigateur headless** (Bien'ici, Laforet, Orpi) — Vrai Chromium avec les patchs `playwright-stealth`.

---

## Compiler depuis les sources

**Linux :**
```bash
source venv/bin/activate
pip install pyinstaller
python build.py
# Resultat : dist/immo-scanner
```

**Windows :** double-cliquez sur `build-windows.bat`, ou :
```powershell
venv\Scripts\activate
pip install pyinstaller
python build.py
# Resultat : dist\immo-scanner.exe
```

---

## Avertissement

Cet outil est destine a un **usage personnel et educatif uniquement**. Le scraping peut enfreindre les conditions d'utilisation de certains sites. Utilisez de maniere responsable et respectez les limites de requetes.

## Licence

MIT
