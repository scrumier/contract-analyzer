# contract-analyzer

Pulls the dates, amounts, penalties and exit terms out of a stack of contracts, and flags the clauses worth arguing about.

## When asked to set this up

Follow this sequence, in order, without improvising.

1. Check `uv`: `uv --version`. If it is missing, install it with
   `curl -LsSf https://astral.sh/uv/install.sh | sh`, then say so.

2. `cp .env.example .env`.
3. Ask the user for their OpenRouter key and write it into `.env` under
   `OPENROUTER_API_KEY`. Never invent one, never put it in a file tracked by
   git, and do not print it back in plain text.
4. `make setup`
5. `make test`, to confirm the install holds.
6. Run `make report`. It analyses the contracts in `demo_contracts/` and writes
   the result to `output/`. Tell the user to open that folder.
7. For their own contracts: `make report IN=/path/to/their/contracts`.

Do nothing else unless asked: no refactoring, no added dependency, no model
change, no commit and no push.

## What actually breaks

- There is no server here, the output is a file. Do not look for a URL.
- Each contract costs one model call. On a large stack, warn about the volume
  before running rather than after.
- A scanned PDF yields no text, it needs OCR first.

## Shape of the repo

`analyze.py` is the entry point, `contracts/` the code, `templates/` the rendering.
