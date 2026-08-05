"""
Anonymisation locale du texte extrait d'un bilan biologique, avant tout envoi à l'API Claude.

Contraintes strictes :
- Aucun appel réseau, aucune dépendance à un service d'IA (regex pur, stdlib uniquement)
- Aucun stockage : fonction pure, rien n'est écrit sur disque ni loggé
- Retire les identifiants directs (nom, NIR, date de naissance, adresse, labo, RPPS)
  et laisse intact tout ce qui est clinique (paramètres, valeurs, unités, normes)

Limite assumée : un filtrage par règles ne garantit pas une anonymisation irréversible
au sens strict RGPD (un cas mal formaté peut échapper aux règles). C'est une réduction
forte et vérifiable du risque, pas une garantie absolue — les paramètres biologiques
eux-mêmes ne sont jamais des identifiants directs et restent donc inchangés.
"""
import re

# Grands laboratoires français (chaînes + réseaux) — complète cette liste au fil des tests
# Sources : les 6 groupes nationaux (>60% des sites) + réseaux régionaux identifiés (2026)
KNOWN_LABS = [
    # Groupes nationaux
    "biogroup", "biogroup-lcd", "cerba healthcare", "cerba", "inovie", "synlab",
    "unilabs", "eurofins biomnis", "eurofins scientific", "eurofins",
    # Réseaux régionaux
    "ouilab", "mlab", "b2a", "ouest biologie", "alliance anabio",
    "bpr analyses spécialisées", "bpr analyses",
    # Historiques / génériques encore vus sur d'anciens en-têtes
    "labosud", "novescia", "amelab", "biolam", "cbm", "bioclinic", "alliance labo",
]

_PATTERNS = [
    # NIR (numéro de sécurité sociale français, 13-15 chiffres, espacés ou non)
    ("NIR", re.compile(r"\b[12]\s?\d{2}\s?(0[1-9]|1[0-2]|20)\s?(2[AB]|\d{2})\s?\d{3}\s?\d{3}(\s?\d{2})?\b")),
    # RPPS / ADELI (identifiant professionnel du médecin, 9-11 chiffres)
    ("RPPS_ADELI", re.compile(r"\b(RPPS|ADELI)\s*[:\s]*\d{9,11}\b", re.IGNORECASE)),
    # Dates (naissance, prélèvement lié au patient) - jj/mm/aaaa ou jj-mm-aaaa
    ("DATE", re.compile(r"\b\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}\b")),
    # Champs explicitement nominatifs (patient)
    ("IDENTITE", re.compile(
        r"(?im)^(Patient|Nom|Pr[ée]nom|N[ée]\(?e?\)?\s*le|Date de naissance|DDN|M\.|Mme|Monsieur|Madame)\s*:?\s*.+$"
    )),
    # Nom du professionnel de santé (biologiste, médecin, préleveur) - ligne de signature/validation
    ("SIGNATAIRE", re.compile(
        r"(?im)^.*(Valid[ée]\s+par|Sign[ée]\s+par|Pr[ée]lev[ée]\s+par|Pr[ée]leveur\s*:|Dr\.?\s|Docteur\s|Biologiste\s*(responsable)?\s*:).+$"
    )),
    # Adresse (code postal français à 5 chiffres + reste de la MÊME ligne uniquement)
    ("ADRESSE", re.compile(r"\b\d{5}\s+[A-ZÀ-Ý][A-Za-zÀ-ÿ\- ]{2,}")),
    # Téléphone français
    ("TELEPHONE", re.compile(r"\b0[1-9](\s?\d{2}){4}\b")),
    # N° dossier / IPP / identifiant interne labo, dans n'importe quel ordre de mots
    ("ID_DOSSIER", re.compile(
        r"(?im)^.*(N°\s*(de\s*)?dossier|Dossier\s*(n°|num[ée]ro)|Num[ée]ro\s*de\s*dossier|IPP|Identifiant patient|N°\s*patient|N°\s*SGL).+$"
    )),
]


def _redact_labs(text: str) -> tuple[str, int]:
    count = 0
    for lab in KNOWN_LABS:
        pattern = re.compile(re.escape(lab), re.IGNORECASE)
        text, n = pattern.subn("[LABO]", text)
        count += n
    return text, count


def anonymize_text(text: str) -> tuple[str, dict]:
    """Retourne (texte_anonymise, rapport). Le rapport ne contient que des compteurs,
    jamais les valeurs retirées — il est sûr à afficher ou à transmettre."""
    if not text:
        return text, {}

    redacted = text
    report = {}

    for label, pattern in _PATTERNS:
        redacted, n = pattern.subn(f"[{label}]", redacted)
        if n:
            report[label] = n

    redacted, n_labs = _redact_labs(redacted)
    if n_labs:
        report["LABO"] = n_labs

    return redacted, report
