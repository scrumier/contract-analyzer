# contract-analyzer

**Problem:** nobody actually reads the 40-page supplier contracts. Until the penalty clause does.<br>
**Solution:** get back the parties, dates, amounts, penalties and termination terms, with the risky clauses flagged.

Output is an HTML report anyone can read.

## Run it

```bash
cp .env.example .env    # add your OPENROUTER_API_KEY
make setup
make report             # analyses demo_contracts/ into output/
make report IN=mes-contrats/
```

Demo contracts are included. Point it at your own folder, or at a single PDF.

`make test` runs the suite, `make lint` runs Ruff.

## How it works

pdfplumber pulls the text and Claude returns the clauses as structured fields. What comes back is validated against a schema first, so a contract the model failed to read is reported as failed instead of quietly becoming an empty card.

Then fixed rules, no model involved, decide what deserves attention:

- payment terms above the legal ceiling: 60 days from the invoice date, or 45 days end-of-month when the contract stipulates it ([code de commerce, art. L441-10](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000038414392))
- a contract already expired, or ending within 90 days
- no termination clause, no price revision clause, no late penalties

Every flag names the rule that raised it, so you can argue with the rule.

The model also volunteers its own remarks. Those are shown in a separate box, labelled unverified, because nothing checks them.

## What it won't do

This is not legal review. It tells you where to look, not what to sign.

## This is the level 1

It works on a folder of PDFs you gathered yourself.

The version that actually saves money is the one plugged into where the contracts already live, that warns you 60 days before a renewal fires instead of the day you remember to run it. Building that around your stack is what I do.

[LinkedIn](https://www.linkedin.com/in/sonam-crumiere) · [sonam.me](https://sonam.me)
