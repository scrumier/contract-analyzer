from datetime import date

import pytest

from contracts.models import ExtractedContract
from contracts.rules import (
    SEVERITY_HIGH,
    evaluate,
    parse_date,
    parse_payment_days,
)

TODAY = date(2026, 7, 1)

# A contract with nothing to report, used as the baseline every test bends.
CLEAN = {
    "fournisseur": "Rocmer",
    "date_debut": "01/01/2026",
    "date_fin": "31/12/2027",
    "conditions_paiement": "30 jours à réception de facture",
    "revision_prix": "Indexation annuelle sur l'indice BT01",
    "penalites_retard": "0,5% du montant par semaine de retard",
    "resiliation": "Préavis de 3 mois par lettre recommandée",
}


def _contract(**overrides):
    return ExtractedContract(**{**CLEAN, **overrides})


def _codes(contract, today=TODAY):
    return {finding.code for finding in evaluate(contract, today=today)}


def test_a_complete_contract_raises_nothing():
    assert _codes(_contract()) == set()


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("30 jours à réception", (30, False)),
        ("60 jours fin de mois", (60, True)),
        ("paiement à 45 J", (45, False)),
        ("Fin de mois, 45 jours", (45, True)),
        ("paiement comptant", None),
        (None, None),
    ],
)
def test_payment_days_are_read_out_of_free_text(value, expected):
    assert parse_payment_days(value) == expected


def test_payment_over_sixty_days_is_flagged():
    assert "paiement_hors_plafond" in _codes(
        _contract(conditions_paiement="90 jours à réception")
    )


def test_payment_at_the_legal_ceiling_is_not_flagged():
    assert "paiement_hors_plafond" not in _codes(
        _contract(conditions_paiement="60 jours à réception")
    )


def test_end_of_month_terms_use_the_lower_ceiling():
    # 60 days is fine as a plain term, but the end-of-month derogation caps at 45.
    assert "paiement_hors_plafond" in _codes(
        _contract(conditions_paiement="60 jours fin de mois")
    )


def test_forty_five_days_end_of_month_is_allowed():
    assert "paiement_hors_plafond" not in _codes(
        _contract(conditions_paiement="45 jours fin de mois")
    )


def test_unreadable_payment_terms_are_not_flagged():
    # No duration to compare against, so the rule stays silent rather than guessing.
    assert "paiement_hors_plafond" not in _codes(
        _contract(conditions_paiement="paiement comptant")
    )


def test_expired_contract_is_flagged():
    assert "expire" in _codes(_contract(date_fin="01/01/2026"))


def test_contract_ending_soon_is_flagged():
    assert "echeance_proche" in _codes(_contract(date_fin="15/08/2026"))


def test_contract_ending_far_out_is_not_flagged():
    assert _codes(_contract(date_fin="31/12/2027")) == set()


def test_missing_end_date_is_flagged():
    assert "sans_date_fin" in _codes(_contract(date_fin=None))


def test_unparseable_end_date_counts_as_missing():
    assert "sans_date_fin" in _codes(_contract(date_fin="courant 2027"))


@pytest.mark.parametrize(
    ("field", "code"),
    [
        ("resiliation", "sans_resiliation"),
        ("revision_prix", "sans_revision_prix"),
        ("penalites_retard", "sans_penalites"),
    ],
)
def test_a_missing_clause_is_reported(field, code):
    assert code in _codes(_contract(**{field: None}))


def test_the_string_null_counts_as_missing():
    assert "sans_resiliation" in _codes(_contract(resiliation="null"))


def test_findings_are_ordered_most_severe_first():
    findings = evaluate(_contract(date_fin="01/01/2026", resiliation=None), today=TODAY)

    assert findings[0].severity == SEVERITY_HIGH


def test_every_finding_explains_itself():
    findings = evaluate(_contract(date_fin=None, resiliation=None), today=TODAY)

    assert all(finding.label and finding.detail for finding in findings)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("31/12/2027", date(2027, 12, 31)),
        ("31-12-2027", date(2027, 12, 31)),
        ("2027-12-31", date(2027, 12, 31)),
        ("pas une date", None),
        (None, None),
    ],
)
def test_dates_are_read_in_the_formats_contracts_use(value, expected):
    assert parse_date(value) == expected
