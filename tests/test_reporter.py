from contracts.models import ExtractedContract
from contracts.reporter import ContractResult, generate_report
from contracts.rules import SEVERITY_HIGH, Finding


def _result(**overrides):
    base = {
        "filename": "contrat-rocmer.pdf",
        "contract": ExtractedContract(
            fournisseur="Rocmer",
            date_debut="01/01/2026",
            date_fin="31/12/2027",
            conditions_paiement="30 jours",
        ),
        "findings": [],
    }
    return ContractResult(**{**base, **overrides})


def _render(tmp_path, results):
    output = tmp_path / "report.html"
    generate_report(results, str(output))
    return output.read_text(encoding="utf-8")


def test_title_falls_back_to_the_filename():
    result = _result(contract=ExtractedContract(fournisseur=None))

    assert result.title == "contrat-rocmer"


def test_title_uses_the_supplier_when_known():
    assert _result().title == "Rocmer"


def test_period_is_none_when_no_date_was_found():
    result = _result(contract=ExtractedContract())

    assert result.period is None


def test_period_marks_the_missing_bound():
    result = _result(contract=ExtractedContract(date_debut="01/01/2026"))

    assert result.period == "01/01/2026 → ?"


def test_rows_skip_fields_the_model_did_not_find():
    labels = [label for label, _ in _result().rows]

    assert "Fournisseur" in labels
    assert "Garanties" not in labels


def test_report_escapes_extracted_values(tmp_path):
    hostile = _result(
        contract=ExtractedContract(fournisseur="<script>alert(1)</script>")
    )

    html = _render(tmp_path, [hostile])

    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_report_shows_the_findings(tmp_path):
    finding = Finding(
        code="expire",
        label="Contrat expiré",
        detail="Terme dépassé depuis le 01/01/2026",
        severity=SEVERITY_HIGH,
    )

    html = _render(tmp_path, [_result(findings=[finding])])

    assert "Contrat expiré" in html
    assert "Terme dépassé" in html


def test_a_failed_contract_says_so_instead_of_vanishing(tmp_path):
    failed = ContractResult(filename="illisible.pdf", error="JSON invalide")

    html = _render(tmp_path, [failed])

    assert "illisible.pdf" in html
    assert "Extraction échouée" in html


def test_model_remarks_are_labelled_as_unverified(tmp_path):
    result = _result(
        contract=ExtractedContract(fournisseur="Rocmer", alertes=["Clause floue"])
    )

    html = _render(tmp_path, [result])

    assert "Clause floue" in html
    assert "non vérifiées" in html


def test_counters_add_up(tmp_path):
    finding = Finding(code="x", label="L", detail="D", severity=SEVERITY_HIGH)
    results = [
        _result(findings=[finding, finding]),
        ContractResult(filename="ko.pdf", error="boom"),
    ]

    html = _render(tmp_path, results)

    assert "<p>2</p>" in html  # 2 contracts
    assert "<p>1</p>" in html  # 1 extraction failure
