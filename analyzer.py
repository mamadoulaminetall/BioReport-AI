import anthropic
import base64
import os
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """Tu es un expert en biologie médicale. Tu analyses des résultats de bilan biologique et tu rédiges un rapport d'interprétation structuré à destination du médecin prescripteur.

Ton rapport doit toujours contenir ces 4 sections :

## 1. Résumé des anomalies
Liste uniquement les valeurs hors normes avec leur degré de gravité :
- 🟡 Légère : déviation < 20% de la norme
- 🟠 Modérée : déviation 20–50%
- 🔴 Critique : déviation > 50% ou valeur d'alerte clinique

Si toutes les valeurs sont normales, indique : ✅ Bilan dans les limites de la normale.

## 2. Interprétation clinique
Explique ce que ces résultats signifient cliniquement. Regroupe les anomalies par tableau (ex: syndrome inflammatoire, anémie microcytaire, insuffisance rénale...). Si le contexte patient est fourni, tiens compte de l'âge, du sexe, des antécédents et des traitements en cours pour affiner l'interprétation.

## 3. Diagnostics à évoquer
Liste les principales hypothèses diagnostiques selon le tableau biologique, du plus probable au moins probable. Indique si un traitement en cours peut expliquer ou masquer une anomalie.

## 4. Recommandations
Propose les actions à envisager : contrôle biologique, examens complémentaires, délai de prise en charge, avis spécialisé. Si un traitement en cours est potentiellement impliqué, signale-le.

Règles strictes :
- Langue : français médical, clair et concis
- Ne jamais poser de diagnostic certain
- Terminer par : "⚠️ Cette interprétation est une aide à la décision. Le diagnostic final appartient au médecin prescripteur."
"""


def _build_context_block(patient_ctx: dict | None, treatments_text: str | None) -> str:
    parts = []
    if patient_ctx:
        p = []
        if patient_ctx.get("age"):
            p.append(f"Âge : {patient_ctx['age']} ans")
        if patient_ctx.get("sexe"):
            p.append(f"Sexe : {patient_ctx['sexe']}")
        if patient_ctx.get("motif"):
            p.append(f"Motif de prescription : {patient_ctx['motif']}")
        if patient_ctx.get("antecedents"):
            p.append(f"Antécédents : {patient_ctx['antecedents']}")
        if p:
            parts.append("**Contexte patient :**\n" + "\n".join(p))
    if treatments_text:
        parts.append(f"**Traitements en cours :**\n{treatments_text}")
    return "\n\n".join(parts)


def _client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def extract_treatments(image_bytes: bytes, media_type: str) -> str:
    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    msg = _client().messages.create(
        model="claude-opus-4-7",
        max_tokens=600,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": media_type, "data": b64},
                    },
                    {
                        "type": "text",
                        "text": "Extrais la liste complète des médicaments visibles (nom, dosage, posologie si présents). Réponds uniquement avec la liste, sans commentaire.",
                    },
                ],
            }
        ],
    )
    return msg.content[0].text


def analyze(raw_text: str, patient_ctx: dict | None = None, treatments_text: str | None = None) -> str:
    ctx = _build_context_block(patient_ctx, treatments_text)
    user_msg = ""
    if ctx:
        user_msg += f"{ctx}\n\n"
    user_msg += f"Voici les résultats du bilan biologique à analyser :\n\n{raw_text}"

    msg = _client().messages.create(
        model="claude-opus-4-7",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    return msg.content[0].text


def analyze_image(image_bytes: bytes, media_type: str, patient_ctx: dict | None = None, treatments_text: str | None = None) -> str:
    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    ctx = _build_context_block(patient_ctx, treatments_text)
    text_part = "Voici la photo d'un compte-rendu de bilan biologique. Extrais toutes les valeurs visibles et rédige le rapport d'interprétation structuré."
    if ctx:
        text_part = f"{ctx}\n\n{text_part}"

    msg = _client().messages.create(
        model="claude-opus-4-7",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": media_type, "data": b64},
                    },
                    {"type": "text", "text": text_part},
                ],
            }
        ],
    )
    return msg.content[0].text
