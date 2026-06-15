import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """Tu es un expert juridique spécialisé en contrats fournisseurs BTP/matériaux.
Extrais les clauses clés du contrat fourni et retourne UNIQUEMENT un objet JSON valide, sans markdown, sans explication.

Structure exacte à retourner :
{
  "fournisseur": "nom du fournisseur",
  "acheteur": "nom de l'acheteur (ACME ou groupe)",
  "date_debut": "JJ/MM/AAAA ou null",
  "date_fin": "JJ/MM/AAAA ou null",
  "montant_total": "montant en € ou null si non spécifié",
  "conditions_paiement": "délai et mode de paiement",
  "revision_prix": "clause de révision tarifaire ou null",
  "penalites_retard": "taux ou montant des pénalités ou null",
  "resiliation": "conditions de résiliation (préavis, motifs)",
  "garanties": "garanties produits / SAV mentionnées ou null",
  "alertes": ["liste de points de vigilance à signaler au DAF"]
}"""


def extract_clauses(contract_text: str, filename: str) -> dict:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )
    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL", "anthropic/claude-haiku-4-5"),
        max_tokens=1000,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Contrat : {filename}\n\n{contract_text[:8000]}"},
        ],
    )
    raw = response.choices[0].message.content.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"error": "Extraction échouée", "raw": raw[:200]}
