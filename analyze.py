import argparse
import os
from datetime import datetime
from pathlib import Path

from contracts.loader import load_contracts
from contracts.extractor import extract_clauses
from contracts.reporter import generate_report


def main():
    parser = argparse.ArgumentParser(description="Analyse contrats fournisseurs ACME")
    parser.add_argument("input", help="Dossier contenant les PDFs ou chemin vers un seul PDF")
    parser.add_argument("output", help="Dossier de sortie")
    args = parser.parse_args()

    Path(args.output).mkdir(parents=True, exist_ok=True)

    # Load contracts
    input_path = Path(args.input)
    if input_path.is_file():
        from contracts.loader import extract_text
        contracts = [{"filename": input_path.name, "text": extract_text(str(input_path))}]
    else:
        contracts = load_contracts(args.input)

    if not contracts:
        print("Aucun PDF trouvé.")
        return

    print(f"{len(contracts)} contrat(s) chargé(s). Extraction en cours...")

    results = []
    for i, contract in enumerate(contracts, 1):
        print(f"  [{i}/{len(contracts)}] {contract['filename']}...")
        data = extract_clauses(contract["text"], contract["filename"])
        results.append({"filename": contract["filename"], "data": data})

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_path = os.path.join(args.output, f"rapport-contrats-{timestamp}.html")
    generate_report(results, output_path)
    print(f"\nRapport généré : {output_path}")


if __name__ == "__main__":
    main()
