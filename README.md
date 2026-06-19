# Immo-Scanner

Scanner d'annonces immobilières pour trouver les meilleurs biens pour investissement locatif en France.

## Fonctionnalités

- **8 sites scannés** : LeBonCoin, SeLoger, PAP, Bien'ici, Logic-Immo, ParuVendu, Figaro Immo, Ouestfrance-Immo
- **Scoring intelligent** : rendement brut/net, prix/m² vs zone, tension locative, typologie optimale
- **2 modes d'estimation de loyer** : base intégrée (50 villes) + cross-référence annonces location
- **Export Excel** avec 3 onglets (classement, détails, statistiques) + mise en forme conditionnelle
- **Déduplication** automatique cross-sites
- **Anti-bot** : rate limiting, rotation User-Agent, cloudscraper, proxy, retry

## Installation

```bash
git clone https://github.com/mattow02/immo-scanner.git
cd immo-scanner
python -m venv venv
source venv/bin/activate
pip install -e .
```

## Configuration

```bash
cp .env.example .env
# Éditer .env avec vos paramètres
```

## Utilisation

```bash
# Scan complet (utilise la config .env)
immo-scanner scan

# Overrides en ligne de commande
immo-scanner scan --city Lyon --budget-max 150000 --min-yield 7
immo-scanner scan --city Paris --city Lyon --types apartment --max-pages 3
immo-scanner scan --department 69 --types apartment,house

# Afficher la config active
immo-scanner config

# Lister les sites disponibles
immo-scanner sites
```

### Options du scan

| Option | Description |
|--------|-------------|
| `--city` | Ville(s) à scanner (répétable) |
| `--department` | Département(s) à scanner (répétable) |
| `--budget-min` | Budget minimum (€) |
| `--budget-max` | Budget maximum (€) |
| `--surface-min` | Surface minimum (m²) |
| `--surface-max` | Surface maximum (m²) |
| `--types` | Types : apartment, house, building |
| `--min-yield` | Rendement brut minimum (%) |
| `--sites` | Sites à scraper (séparés par virgules) |
| `--max-pages` | Pages max par site |
| `--rental-mode` | avg_price, cross_ref, ou both |
| `-o, --output` | Dossier de sortie Excel |
| `--no-excel` | Pas d'export Excel |
| `-v, --verbose` | Logs détaillés |

## Critères de scoring

| Critère | Poids | Description |
|---------|-------|-------------|
| Rendement brut | 40% | (loyer annuel / prix achat) × 100 |
| Prix/m² vs zone | 15% | Comparaison avec la moyenne de la ville |
| Tension locative | 15% | Demande locative de la zone |
| Typologie | 10% | Studios et T2 favorisés (plus facile à louer) |
| Surface cohérente | 10% | Adéquation surface/nombre de pièces |
| Fraîcheur annonce | 10% | Annonces récentes favorisées |

## Export Excel

Le fichier `.xlsx` généré contient 3 onglets :
1. **Classement** — Top biens triés par score, avec liens cliquables
2. **Détails** — Toutes les données brutes + décomposition du score
3. **Statistiques** — Résumé global, répartition par ville et par source
