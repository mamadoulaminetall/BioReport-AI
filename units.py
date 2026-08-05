"""
Vérification déterministe des valeurs à seuil critique absolu.

Le LLM fait l'extraction et l'interprétation (il est bon pour lire des formats
variés) — mais l'arithmétique de conversion d'unité ne doit jamais reposer
uniquement sur lui pour les valeurs où une erreur peut faire manquer une
alerte critique. Ce module reparse la sortie STRUCTURÉE du LLM (le format de
la section "## 1. Résumé des anomalies" est fixé par notre propre prompt,
donc fiable à parser) et recalcule indépendamment, en Python pur, si le seuil
CLSI/clinique absolu est franchi.

Ne corrige jamais silencieusement le rapport — signale une divergence pour
qu'un humain vérifie. Aide à la décision, jamais un substitut.
"""
import re

# (valeur_min, valeur_max) = intervalle NORMAL/non-critique en unité canonique.
# En dehors de cet intervalle = seuil critique absolu (🔴), selon le prompt système.
CRITICAL_THRESHOLDS = {
    "sodium":     {"aliases": ["na+", "natrémie", "sodium"], "canonical": "mmol/L", "low": 120, "high": 160},
    "potassium":  {"aliases": ["k+", "kaliémie", "potassium"], "canonical": "mmol/L", "low": 2.5, "high": 6.5},
    "calcium":    {"aliases": ["ca2+", "calcémie", "calcium"], "canonical": "mmol/L", "low": 1.5, "high": 3.5},
    "hemoglobine":{"aliases": ["hb", "hémoglobine", "hemoglobine"], "canonical": "g/dL", "low": 7.0, "high": None},
    "glucose":    {"aliases": ["glycémie", "glucose"], "canonical": "mmol/L", "low": 2.2, "high": 33},
    "creatinine": {"aliases": ["créatinine", "creatinine"], "canonical": "µmol/L", "low": None, "high": 500},
    "inr":        {"aliases": ["inr"], "canonical": "", "low": None, "high": 4.0},
    "plaquettes": {"aliases": ["plaquettes", "plt"], "canonical": "G/L", "low": 20, "high": None},
    "ph":         {"aliases": ["ph artériel", "ph"], "canonical": "", "low": 7.15, "high": 7.60},
    "lactates":   {"aliases": ["lactates", "lactate"], "canonical": "mmol/L", "low": None, "high": 4.0},
}

# Facteurs de conversion vers l'unité canonique de chaque paramètre.
# conversion(value, from_unit) -> value_en_unite_canonique
_CONVERTERS = {
    "hemoglobine": {"g/l": lambda v: v / 10},                              # g/L -> g/dL
    "glucose":     {"g/l": lambda v: v * 5.551},                            # g/L -> mmol/L
    "creatinine":  {"mg/l": lambda v: v * 8.84, "mg/dl": lambda v: v * 88.4},  # -> µmol/L
    "calcium":     {"mg/dl": lambda v: v * 0.2495},                         # -> mmol/L
    "lactates":    {"mg/dl": lambda v: v * 0.111},                          # -> mmol/L
    "plaquettes":  {"/mm3": lambda v: v / 1000, "/µl": lambda v: v / 1000},  # -> G/L
}

_RESULT_LINE = re.compile(
    r"\*\*(?P<param>[^*]+)\*\*\s*:\s*(?P<value>[\d,.]+)\s*(?P<unit>[^\s(]+)?\s*\(.*?→\s*(?P<severity>🟡|🟠|🔴)",
    re.IGNORECASE,
)


def _match_param(name: str) -> str | None:
    name_low = name.strip().lower()
    for key, meta in CRITICAL_THRESHOLDS.items():
        if any(alias in name_low for alias in meta["aliases"]):
            return key
    return None


def _to_canonical(param: str, value: float, unit: str) -> float:
    unit_norm = (unit or "").strip().lower().replace("μ", "µ")
    converters = _CONVERTERS.get(param, {})
    for unit_key, fn in converters.items():
        if unit_key in unit_norm:
            return fn(value)
    return value  # déjà dans l'unité canonique (ou unité non reconnue -> pas de conversion)


def check_critical_values(report_text: str) -> list[str]:
    """Reparse les lignes de résultats du rapport et recalcule indépendamment
    si un seuil critique absolu est franchi. Retourne une liste de messages
    d'alerte si le LLM a classé une valeur autrement que ce que le calcul
    déterministe indique — liste vide si tout concorde (ou si rien à vérifier)."""
    warnings = []
    for m in _RESULT_LINE.finditer(report_text):
        param = _match_param(m.group("param"))
        if not param:
            continue
        try:
            value = float(m.group("value").replace(",", "."))
        except ValueError:
            continue

        meta = CRITICAL_THRESHOLDS[param]
        canonical_value = _to_canonical(param, value, m.group("unit") or "")
        llm_severity = m.group("severity")

        is_critical = (
            (meta["low"] is not None and canonical_value < meta["low"]) or
            (meta["high"] is not None and canonical_value > meta["high"])
        )

        if is_critical and llm_severity != "🔴":
            warnings.append(
                f"⚠️ Vérification indépendante : {m.group('param').strip()} = {m.group('value')} "
                f"{m.group('unit') or ''} (≈ {canonical_value:.2f} {meta['canonical']}) franchit le seuil critique "
                f"absolu, mais le rapport l'a classé {llm_severity}. À vérifier manuellement."
            )
        elif not is_critical and llm_severity == "🔴":
            warnings.append(
                f"⚠️ Vérification indépendante : {m.group('param').strip()} = {m.group('value')} "
                f"{m.group('unit') or ''} (≈ {canonical_value:.2f} {meta['canonical']}) ne semble pas franchir "
                f"le seuil critique absolu d'après le calcul indépendant, mais le rapport l'a classé 🔴 CRITIQUE. "
                f"À vérifier — l'unité d'origine a peut-être été mal interprétée."
            )

    return warnings
