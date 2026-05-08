from datetime import datetime


def _field(label: str, value) -> str:
    if not value or value == "null":
        return ""
    return f"<tr><td style='color:#6b7280;font-size:12px;padding:4px 0;width:180px'>{label}</td><td style='font-size:13px;padding:4px 0'>{value}</td></tr>"


def _contract_card(data: dict, filename: str) -> str:
    if "error" in data:
        return f"<div class='card error'><strong>{filename}</strong> — extraction échouée</div>"

    alertes = data.get("alertes") or []
    alert_html = ""
    if alertes:
        items = "".join(f"<li>{a}</li>" for a in alertes)
        alert_html = f"<div class='alert'><strong>Points de vigilance :</strong><ul>{items}</ul></div>"

    rows = "".join([
        _field("Fournisseur", data.get("fournisseur")),
        _field("Acheteur", data.get("acheteur")),
        _field("Période", f"{data.get('date_debut', '?')} → {data.get('date_fin', '?')}"),
        _field("Montant total", data.get("montant_total")),
        _field("Paiement", data.get("conditions_paiement")),
        _field("Révision prix", data.get("revision_prix")),
        _field("Pénalités retard", data.get("penalites_retard")),
        _field("Résiliation", data.get("resiliation")),
        _field("Garanties", data.get("garanties")),
    ])

    name = data.get("fournisseur") or filename.replace(".pdf", "")
    return f"""
<div class='card'>
  <div class='card-header'>
    <span class='card-title'>{name}</span>
    <span style='font-size:11px;color:#9ca3af'>{filename}</span>
  </div>
  <table style='width:100%;border-collapse:collapse;margin-top:8px'>{rows}</table>
  {alert_html}
</div>"""


def generate_report(results: list[dict], output_path: str) -> str:
    cards = "".join(_contract_card(r["data"], r["filename"]) for r in results)
    total = len(results)
    errors = sum(1 for r in results if "error" in r["data"])
    alert_count = sum(len(r["data"].get("alertes") or []) for r in results if "error" not in r["data"])

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Analyse Contrats Fournisseurs - {datetime.now().strftime('%d/%m/%Y')}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: system-ui, sans-serif; background: #f9fafb; color: #1f2937; padding: 32px; max-width: 960px; margin: 0 auto; }}
  h1 {{ font-size: 22px; font-weight: 700; margin-bottom: 4px; }}
  .meta {{ font-size: 13px; color: #6b7280; margin-bottom: 28px; }}
  .stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 28px; }}
  .stat {{ background: white; border: 1px solid #e5e7eb; border-radius: 10px; padding: 16px 20px; }}
  .stat h3 {{ font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #9ca3af; margin-bottom: 6px; }}
  .stat p {{ font-size: 26px; font-weight: 700; }}
  .stat.warn {{ border-left: 4px solid #f59e0b; }}
  .card {{ background: white; border: 1px solid #e5e7eb; border-radius: 10px; padding: 20px 24px; margin-bottom: 16px; }}
  .card.error {{ border-left: 4px solid #ef4444; color: #6b7280; }}
  .card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }}
  .card-title {{ font-size: 15px; font-weight: 600; }}
  .alert {{ background: #fffbeb; border: 1px solid #fde68a; border-radius: 6px; padding: 10px 14px; margin-top: 12px; font-size: 13px; }}
  .alert ul {{ margin-top: 4px; padding-left: 18px; }}
  .alert li {{ margin-top: 3px; color: #92400e; }}
</style>
</head>
<body>
<h1>Analyse Contrats Fournisseurs</h1>
<p class="meta">Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} — {total} contrats analysés</p>

<div class="stats">
  <div class="stat"><h3>Contrats analysés</h3><p>{total}</p></div>
  <div class="stat warn"><h3>Points de vigilance</h3><p>{alert_count}</p></div>
  <div class="stat"><h3>Erreurs extraction</h3><p>{errors}</p></div>
</div>

{cards}
</body>
</html>"""

    with open(output_path, "w") as f:
        f.write(html)
    return output_path
