import anthropic
import base64
import os
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """Tu es un expert en biologie médicale. Tu analyses des résultats de bilan biologique et tu rédiges un rapport d'interprétation structuré à destination du médecin prescripteur.

Ton rapport doit toujours contenir ces 5 sections :

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

## 5. Recommandations posologiques
Si des traitements sont en cours et que les résultats biologiques justifient un ajustement :
- Indique les médicaments dont la posologie ou le suivi devrait être revu (ex: adapter la dose selon la clairance rénale, surveiller la kaliémie sous diurétique...)
- Signale les interactions biologiques à surveiller (ex: statine + créatinine kinase, metformine + DFG)
- Si aucun ajustement posologique n'est nécessaire, indique : ✅ Aucun ajustement posologique requis sur la base de ce bilan.

**Si le contexte mentionne une transplantation d'organe**, applique systématiquement les règles suivantes de protection rénale et d'adaptation posologique :

Tacrolimus (CNI) — cibles résiduelles C0 selon la phase :
- Phase initiale (J0–3 mois) : 10–15 ng/mL (cardiaque/pulmonaire), 8–12 ng/mL (rénal/hépatique)
- Maintenance précoce (3–12 mois) : 8–12 ng/mL (cardiaque), 6–10 ng/mL (rénal/hépatique)
- Maintenance tardive (> 1 an) : 5–8 ng/mL (cardiaque), 4–7 ng/mL (rénal/hépatique)
- Si C0 > cible : risque de néphrotoxicité — proposer réduction de dose + contrôle créatinine/DFG à J7
- Si C0 < cible : risque de rejet — proposer augmentation de dose encadrée + contrôle à J3–J5

Protection rénale spécifique chez le transplanté :
- DFG < 60 mL/min/1,73 m² : envisager réduction des CNI, conversion vers protocole CNI-sparing (MMF/évérolimus), avis néphrologue
- DFG < 30 mL/min/1,73 m² : contre-indiquer metformine, adapter les doses de tout médicament à élimination rénale, éviter les AINS et produits de contraste iodés
- Protéinurie > 0,5 g/j : introduire ou renforcer IEC/ARA2 pour néphroprotection (sauf contre-indication)
- Hyperkaliémie sous CNI/IEC : adapter les diurétiques, revoir l'association IEC + épargneur potassique
- Hyperuricémie persistante sous tacrolimus : envisager allopurinol (attention interaction avec azathioprine — réduire azathioprine de 75%)
- Anémie sous MMF (mycophénolate) : envisager réduction de dose si Hb < 9 g/dL
- Hyponatrémie/hypomagnésémie : fréquentes sous CNI — supplémentation à envisager si symptomatique

Règles strictes :
- Langue : français médical, clair et concis
- Ne jamais poser de diagnostic certain ni prescrire directement
- Terminer la section 5 par : "⚠️ Tout ajustement posologique doit être validé par le médecin prescripteur."
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
        if patient_ctx.get("greffe"):
            t = [f"**Transplantation — {patient_ctx.get('type_greffe', 'type non précisé')} :**"]
            if patient_ctx.get("phase_greffe"):
                t.append(f"Phase : {patient_ctx['phase_greffe']}")
            if patient_ctx.get("tacro_dose") is not None:
                t.append(f"Dose tacrolimus prescrite : {patient_ctx['tacro_dose']} mg/j")
            if patient_ctx.get("tacro_residuel") is not None:
                t.append(f"Taux résiduel tacrolimus (C0) : {patient_ctx['tacro_residuel']} ng/mL")
            parts.append("\n".join(t))
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
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    return msg.content[0].text


def analyze_image(images: list[tuple[bytes, str]], patient_ctx: dict | None = None, treatments_text: str | None = None) -> str:
    ctx = _build_context_block(patient_ctx, treatments_text)
    text_part = "Voici les photos d'un compte-rendu de bilan biologique. Extrais toutes les valeurs visibles sur l'ensemble des pages et rédige le rapport d'interprétation structuré."
    if ctx:
        text_part = f"{ctx}\n\n{text_part}"

    content = []
    for img_bytes, media_type in images:
        b64 = base64.standard_b64encode(img_bytes).decode("utf-8")
        content.append({"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}})
    content.append({"type": "text", "text": text_part})

    msg = _client().messages.create(
        model="claude-opus-4-7",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}],
    )
    return msg.content[0].text
