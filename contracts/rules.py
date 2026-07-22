"""Deterministic checks over an extracted contract.

None of this asks the model anything. Every finding below is arithmetic or a
pattern match on what was extracted, so a flag can always be traced back to the
rule that raised it. The model's own opinion travels separately, under
`alertes`, and is labelled as an opinion in the report.
"""

import re
from dataclasses import dataclass
from datetime import date, datetime

from contracts.models import ExtractedContract

# Code de commerce, article L441-10: the agreed payment term cannot exceed 60
# days from the invoice issue date, with a derogation at 45 days end-of-month
# when the contract stipulates it expressly.
# https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000038414392
LEGAL_MAX_DAYS = 60
LEGAL_MAX_DAYS_END_OF_MONTH = 45

# How close to its end date a contract has to be before it is worth putting on
# someone's desk. A quarter is enough time to renegotiate or to give notice.
RENEWAL_WINDOW_DAYS = 90

DATE_FORMATS = ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d")

_DAYS_PATTERN = re.compile(r"(\d{1,3})\s*(?:jours?|j\b)", re.IGNORECASE)
_END_OF_MONTH_PATTERN = re.compile(r"fin\s+de\s+mois", re.IGNORECASE)

SEVERITY_HIGH = "high"
SEVERITY_MEDIUM = "medium"


@dataclass(frozen=True)
class Finding:
    """One thing a rule flagged on one contract."""

    code: str
    label: str
    detail: str
    severity: str


def parse_date(value: str | None) -> date | None:
    """Read a date in any of the formats a contract might print it in.

    Args:
        value: Date as extracted.

    Returns:
        The date, or None if absent or unrecognised.
    """
    if not value:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            continue
    return None


def parse_payment_days(terms: str | None) -> tuple[int, bool] | None:
    """Pull a number of days out of free-text payment terms.

    Args:
        terms: The payment clause as extracted, e.g. "60 jours fin de mois".

    Returns:
        The number of days and whether the clause is end-of-month, or None if
        no duration could be read.
    """
    if not terms:
        return None
    match = _DAYS_PATTERN.search(terms)
    if not match:
        return None
    return int(match.group(1)), bool(_END_OF_MONTH_PATTERN.search(terms))


def _check_payment_terms(contract: ExtractedContract) -> Finding | None:
    """Compare the agreed payment term against the legal ceiling."""
    parsed = parse_payment_days(contract.conditions_paiement)
    if parsed is None:
        return None
    days, end_of_month = parsed

    ceiling = LEGAL_MAX_DAYS_END_OF_MONTH if end_of_month else LEGAL_MAX_DAYS
    if days <= ceiling:
        return None

    basis = "45 jours fin de mois" if end_of_month else "60 jours"
    return Finding(
        code="paiement_hors_plafond",
        label="Délai de paiement au-dessus du plafond légal",
        detail=(
            f"{days} jours convenus, plafond {basis} (code de commerce, art. L441-10)"
        ),
        severity=SEVERITY_HIGH,
    )


def _check_end_date(contract: ExtractedContract, today: date) -> Finding | None:
    """Report a contract that has run out or is about to."""
    end = parse_date(contract.date_fin)
    if end is None:
        return Finding(
            code="sans_date_fin",
            label="Pas de date de fin",
            detail="Engagement sans terme lisible dans le contrat",
            severity=SEVERITY_MEDIUM,
        )
    if end < today:
        return Finding(
            code="expire",
            label="Contrat expiré",
            detail=f"Terme dépassé depuis le {end:%d/%m/%Y}",
            severity=SEVERITY_HIGH,
        )
    remaining = (end - today).days
    if remaining <= RENEWAL_WINDOW_DAYS:
        return Finding(
            code="echeance_proche",
            label="Échéance proche",
            detail=f"Se termine le {end:%d/%m/%Y}, dans {remaining} jours",
            severity=SEVERITY_HIGH,
        )
    return None


def _check_missing_clause(
    value: str | None,
    code: str,
    label: str,
    detail: str,
) -> Finding | None:
    """Report a clause the contract never mentions."""
    if value:
        return None
    return Finding(code=code, label=label, detail=detail, severity=SEVERITY_MEDIUM)


def evaluate(contract: ExtractedContract, today: date | None = None) -> list[Finding]:
    """Run every rule against one contract.

    Args:
        contract: The extracted clauses.
        today: Reference date for the deadline rules. Defaults to today, and
            is injectable so the same contract always tests the same way.

    Returns:
        Every finding, most severe first.
    """
    reference = today or date.today()

    findings = [
        _check_payment_terms(contract),
        _check_end_date(contract, reference),
        _check_missing_clause(
            contract.resiliation,
            "sans_resiliation",
            "Pas de clause de résiliation",
            "Aucune condition de sortie identifiée",
        ),
        _check_missing_clause(
            contract.revision_prix,
            "sans_revision_prix",
            "Pas de clause de révision des prix",
            "Le contrat ne dit pas comment les tarifs peuvent évoluer",
        ),
        _check_missing_clause(
            contract.penalites_retard,
            "sans_penalites",
            "Pas de pénalités de retard",
            "Aucun levier contractuel en cas de retard de livraison",
        ),
    ]

    order = {SEVERITY_HIGH: 0, SEVERITY_MEDIUM: 1}
    return sorted(
        (f for f in findings if f is not None),
        key=lambda finding: order[finding.severity],
    )
