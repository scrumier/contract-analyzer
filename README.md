# samse-contracts

Extraction automatique de clauses clés depuis des contrats fournisseurs PDF. Génère un rapport HTML avec points de vigilance identifiés par IA.

## Ce que ça fait

1. Lit les PDFs de contrats fournisseurs
2. Extrait via LLM (Claude) les clauses structurées :
   - Parties, dates, montant
   - Conditions de paiement, révision de prix
   - Pénalités de retard, conditions de résiliation
   - Garanties et alertes DAF
3. Génère un rapport HTML avec cartes par fournisseur + points de vigilance

## Utilisation

```bash
# Setup
uv sync
cp .env.example .env  # remplir OPENROUTER_API_KEY

# Analyser un dossier de contrats
uv run python analyze.py demo_contracts/ output/
# → ouvrir output/rapport-contrats-*.html

# Analyser un seul contrat
uv run python analyze.py demo_contracts/contrat-rockwool-france-2025.pdf output/
```

## Format de sortie

Pour chaque contrat :
- Fournisseur / Acheteur / Période
- Montant total et conditions de paiement
- Clause de révision tarifaire
- Pénalités de retard (fournisseur et acheteur)
- Conditions de résiliation
- Garanties produits
- **Points de vigilance** : alertes concrètes pour le DAF (tacite reconduction, seuils RFA, réserve de propriété...)

## Architecture

```
analyze.py          → CLI entry point
contracts/
  loader.py         → lecture PDF (pdfplumber)
  extractor.py      → extraction LLM via OpenRouter
  reporter.py       → rapport HTML
demo_contracts/     → 7 contrats fournisseurs de démonstration
```
