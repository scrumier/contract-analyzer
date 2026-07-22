"""Validated shape of what the model extracts from a contract.

Everything the model returns crosses this boundary before the rules or the
report touch it. A response that does not match fails here, rather than
producing a report card that looks filled in and is not.
"""

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

# Models asked for "null" sometimes write the four letters instead of emitting
# a JSON null. Same for a blank string. All three mean "not found".
_ABSENT = {"", "null", "none", "n/a", "non spécifié", "non specifie"}


def _blank_to_none(value: object) -> object:
    """Normalise every way the model says "not found" into None.

    Args:
        value: Raw field value from the JSON response.

    Returns:
        None when the value means absent, otherwise the trimmed value.
    """
    if isinstance(value, str):
        stripped = value.strip()
        return None if stripped.lower() in _ABSENT else stripped
    return value


Text = Annotated[str | None, BeforeValidator(_blank_to_none)]


class ExtractedContract(BaseModel):
    """The clauses read off one supplier contract.

    Every field is optional: a contract that says nothing about penalties is a
    real contract, and "the clause is missing" is exactly what the rules are
    there to report.
    """

    model_config = ConfigDict(extra="ignore")

    fournisseur: Text = None
    acheteur: Text = None
    date_debut: Text = None
    date_fin: Text = None
    montant_total: Text = None
    conditions_paiement: Text = None
    revision_prix: Text = None
    penalites_retard: Text = None
    resiliation: Text = None
    garanties: Text = None

    # What the model itself thought was worth raising. Kept separate from the
    # rule findings, and labelled as such in the report: it is an opinion.
    alertes: list[str] = Field(default_factory=list)
