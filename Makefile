# contract-analyzer
#   make setup    install dependencies (once)
#   make report   analyse the demo contracts
#   make test     run the test suite
#   make lint     lint and format check

IN ?= demo_contracts
OUT ?= output

.PHONY: help setup report test lint

help:
	@echo ""
	@echo "  make setup    install dependencies"
	@echo "  make report   analyse $(IN) into $(OUT)"
	@echo "  make test     run the test suite"
	@echo "  make lint     lint and format check"
	@echo ""

setup:
	@uv sync --quiet
	@echo "==> Ready. Copy .env.example to .env and add your OPENROUTER_API_KEY."

report:
	@uv run python analyze.py $(IN) $(OUT)

test:
	@uv run pytest -q

lint:
	@uv run ruff check .
	@uv run ruff format --check .
