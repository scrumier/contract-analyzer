"""Ask a model to read a contract and return its clauses as structured data."""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import ValidationError

from contracts.models import ExtractedContract

load_dotenv()

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "anthropic/claude-haiku-4.5"
MAX_TOKENS = 1000

# Contracts run long and the clauses that matter sit in the first pages. This
# keeps the call cheap; raise it if a corpus buries termination terms deeper.
MAX_CONTRACT_CHARS = 8000

SYSTEM_PROMPT = """Tu es un expert juridique spécialisé en contrats fournisseurs BTP/matériaux.
Extrais les clauses clés du contrat fourni et retourne UNIQUEMENT un objet JSON valide, sans markdown, sans explication.

Structure exacte à retourner :
{
  "fournisseur": "nom du fournisseur",
  "acheteur": "nom de l'acheteur",
  "date_debut": "JJ/MM/AAAA ou null",
  "date_fin": "JJ/MM/AAAA ou null",
  "montant_total": "montant en € ou null si non spécifié",
  "conditions_paiement": "délai et mode de paiement, en reprenant le nombre de jours tel qu'écrit",
  "revision_prix": "clause de révision tarifaire ou null",
  "penalites_retard": "taux ou montant des pénalités ou null",
  "resiliation": "conditions de résiliation (préavis, motifs)",
  "garanties": "garanties produits / SAV mentionnées ou null",
  "alertes": ["liste de points de vigilance"]
}

N'invente jamais une clause absente : si le contrat n'en parle pas, mets null."""  # noqa: E501


def _strip_code_fence(raw: str) -> str:
    """Remove the Markdown fence the model sometimes wraps the JSON in.

    Args:
        raw: Raw message content.

    Returns:
        The content without its opening and closing fence.
    """
    text = raw.strip()
    if text.startswith("```"):
        text = text.removeprefix("```json").removeprefix("```")
    return text.removesuffix("```").strip()


def extract_clauses(contract_text: str, filename: str) -> ExtractedContract:
    """Read one contract's clauses.

    Args:
        contract_text: Text extracted from the PDF.
        filename: Name of the source file, given to the model as context.

    Returns:
        The validated clauses.

    Raises:
        ValueError: If the model returned no content, content that is not
            valid JSON, or JSON that does not match the expected shape.
    """
    client = OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )
    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL", DEFAULT_MODEL),
        max_tokens=MAX_TOKENS,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Contrat : {filename}\n\n{contract_text[:MAX_CONTRACT_CHARS]}"
                ),
            },
        ],
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError(f"{filename}: réponse vide du modèle")

    raw = _strip_code_fence(content)
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{filename}: JSON invalide ({exc})") from exc

    try:
        return ExtractedContract.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"{filename}: structure inattendue ({exc})") from exc
