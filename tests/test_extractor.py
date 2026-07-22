import re
from unittest.mock import MagicMock, patch

import pytest

from contracts.extractor import extract_clauses

VALID = """{
  "fournisseur": "Rocmer",
  "acheteur": "ACME",
  "date_debut": "01/01/2026",
  "date_fin": "31/12/2027",
  "montant_total": "120 000 €",
  "conditions_paiement": "30 jours",
  "revision_prix": null,
  "penalites_retard": null,
  "resiliation": "Préavis 3 mois",
  "garanties": null,
  "alertes": ["Pas de clause de révision"]
}"""


def _extract(content):
    response = MagicMock()
    response.choices[0].message.content = content
    client = MagicMock()
    client.chat.completions.create.return_value = response
    with patch("contracts.extractor.OpenAI", return_value=client):
        return extract_clauses("texte du contrat", "contrat.pdf")


def test_valid_response_is_parsed():
    contract = _extract(VALID)

    assert contract.fournisseur == "Rocmer"
    assert contract.conditions_paiement == "30 jours"
    assert contract.alertes == ["Pas de clause de révision"]


def test_json_null_becomes_none():
    assert _extract(VALID).revision_prix is None


def test_the_string_null_also_becomes_none():
    assert _extract('{"resiliation": "null"}').resiliation is None


def test_blank_field_becomes_none():
    assert _extract('{"resiliation": "   "}').resiliation is None


def test_values_are_trimmed():
    assert _extract('{"fournisseur": "  Rocmer  "}').fournisseur == "Rocmer"


def test_code_fence_is_stripped():
    assert _extract(f"```json\n{VALID}\n```").fournisseur == "Rocmer"


def test_unknown_fields_are_ignored():
    assert _extract('{"fournisseur": "Rocmer", "invente": 1}').fournisseur == "Rocmer"


def test_missing_alertes_defaults_to_empty():
    assert _extract('{"fournisseur": "Rocmer"}').alertes == []


def test_invalid_json_raises():
    with pytest.raises(ValueError, match="JSON invalide"):
        _extract("ceci n'est pas du json")


def test_empty_response_raises():
    with pytest.raises(ValueError, match="réponse vide"):
        _extract(None)


def test_wrong_shape_raises():
    with pytest.raises(ValueError, match="structure inattendue"):
        _extract('{"alertes": "devrait être une liste"}')


def test_the_filename_is_named_in_the_error():
    with pytest.raises(ValueError, match=re.escape("contrat.pdf")):
        _extract("pas du json")
