# contract-analyzer

**Problem:** nobody actually reads the 40-page supplier contracts. Until the penalty clause does.
**Solution:** get back the parties, dates, amounts, penalties and termination terms, with the risky clauses flagged.

Output is an HTML report anyone can read.

## Run it

```bash
cp .env.example .env    # add your OPENROUTER_API_KEY
uv sync
uv run python analyze.py demo_contracts/ output/
```

Demo contracts are included. Point it at your own folder, or at a single PDF.

## How it works

pdfplumber pulls the text, Claude returns structured fields for each contract, then fixed rules decide what deserves attention: auto-renewal about to trigger, penalty above threshold, missing notice period, empty field where there should be a date.

The flags come from rules, not from the model's opinion. You can always check why something was flagged.

## What it won't do

This is not legal review. It tells you where to look, not what to sign.

## This is the level 1

It works on a folder of PDFs you gathered yourself.

The version that actually saves money is the one plugged into where the contracts already live, that warns you 60 days before a renewal fires instead of the day you remember to run it. Building that around your stack is what I do.

[LinkedIn](https://www.linkedin.com/in/sonam-crumiere) · [sonam.me](https://sonam.me)
