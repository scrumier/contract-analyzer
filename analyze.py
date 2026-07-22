#!/usr/bin/env python3
"""Analyse supplier contracts and write an HTML report.

Usage:
    uv run python analyze.py demo_contracts/ output/
"""

import argparse
import logging
from datetime import datetime
from pathlib import Path

from contracts.extractor import extract_clauses
from contracts.loader import extract_text, load_contracts
from contracts.reporter import ContractResult, generate_report
from contracts.rules import evaluate

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


def _parse_args() -> argparse.Namespace:
    """Read the command line.

    Returns:
        The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Analyse supplier contracts.")
    parser.add_argument("input", help="Folder of PDFs, or a single PDF")
    parser.add_argument(
        "output",
        nargs="?",
        default="output",
        help="Where to write the report (default: output/)",
    )
    return parser.parse_args()


def _load(input_path: Path) -> list[dict]:
    """Read the contracts to analyse.

    Args:
        input_path: A PDF, or a folder of PDFs.

    Returns:
        One entry per contract, with its filename and text.
    """
    if input_path.is_file():
        return [{"filename": input_path.name, "text": extract_text(str(input_path))}]
    return load_contracts(str(input_path))


def analyse(input_path: str, output_dir: str) -> str | None:
    """Extract, apply the rules, and write the report.

    One contract failing does not stop the others: the failure is recorded on
    its own card so the report says what was not read, instead of leaving a
    silent hole.

    Args:
        input_path: A PDF, or a folder of PDFs.
        output_dir: Directory the report is written to, created if missing.

    Returns:
        Path of the report, or None if there was nothing to analyse.
    """
    contracts = _load(Path(input_path))
    if not contracts:
        return None

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    results = []
    for position, contract in enumerate(contracts, start=1):
        filename = contract["filename"]
        log.info("  [%d/%d] %s", position, len(contracts), filename)
        try:
            extracted = extract_clauses(contract["text"], filename)
        except ValueError as exc:
            log.warning("      échec: %s", exc)
            results.append(ContractResult(filename=filename, error=str(exc)))
            continue
        results.append(
            ContractResult(
                filename=filename,
                contract=extracted,
                findings=evaluate(extracted),
            )
        )

    timestamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    return generate_report(
        results,
        str(Path(output_dir) / f"rapport-contrats-{timestamp}.html"),
    )


def main() -> None:
    """Run the analysis from the command line."""
    args = _parse_args()

    report_path = analyse(args.input, args.output)
    if report_path is None:
        log.info("Aucun PDF trouvé.")
        return

    log.info("\nRapport généré : %s", report_path)


if __name__ == "__main__":
    main()
