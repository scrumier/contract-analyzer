"""Render the analysed contracts as an HTML report."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from contracts.models import ExtractedContract
from contracts.rules import Finding

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"

FIELD_LABELS = (
    ("fournisseur", "Fournisseur"),
    ("acheteur", "Acheteur"),
    ("montant_total", "Montant total"),
    ("conditions_paiement", "Paiement"),
    ("revision_prix", "Révision prix"),
    ("penalites_retard", "Pénalités retard"),
    ("resiliation", "Résiliation"),
    ("garanties", "Garanties"),
)


@dataclass
class ContractResult:
    """One contract as it came out of the pipeline.

    Either it was read and has findings, or it failed and carries the reason.
    """

    filename: str
    contract: ExtractedContract | None = None
    findings: list[Finding] = field(default_factory=list)
    error: str | None = None

    @property
    def title(self) -> str:
        """Name to show on the card.

        Returns:
            The supplier name, falling back to the file name.
        """
        if self.contract and self.contract.fournisseur:
            return self.contract.fournisseur
        return self.filename.removesuffix(".pdf")

    @property
    def period(self) -> str | None:
        """Contract period, when at least one bound is known.

        Returns:
            A "start to end" string, or None if neither date was found.
        """
        if not self.contract:
            return None
        start, end = self.contract.date_debut, self.contract.date_fin
        if not start and not end:
            return None
        return f"{start or '?'} → {end or '?'}"

    @property
    def rows(self) -> list[tuple[str, str]]:
        """The populated clause fields, in display order.

        Returns:
            Label and value pairs, skipping anything the model did not find.
        """
        if not self.contract:
            return []
        return [
            (label, getattr(self.contract, name))
            for name, label in FIELD_LABELS
            if getattr(self.contract, name)
        ]


def generate_report(results: list[ContractResult], output_path: str) -> str:
    """Write the HTML report.

    Args:
        results: One entry per contract, analysed or failed.
        output_path: Where to write the report.

    Returns:
        The path that was written.
    """
    environment = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html"]),
    )
    html = environment.get_template("report.html").render(
        generated_at=datetime.now().astimezone(),
        results=results,
        total=len(results),
        finding_count=sum(len(r.findings) for r in results),
        error_count=sum(1 for r in results if r.error),
    )
    Path(output_path).write_text(html, encoding="utf-8")
    return output_path
