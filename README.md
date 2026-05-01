# 🧬 BioReport AI

**Interprétation automatique de bilan biologique par IA — pour les laboratoires et médecins prescripteurs.**

[![Streamlit](https://img.shields.io/badge/Streamlit-Cloud-FF4B4B?logo=streamlit&logoColor=white)](https://bioreport-ai.streamlit.app)
[![Claude](https://img.shields.io/badge/Powered%20by-Claude%20Opus-6B21A8?logo=anthropic&logoColor=white)](https://console.anthropic.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/Licence-MIT-22c55e)](LICENSE)

🚀 **[Accéder à l'application → bioreport-ai.streamlit.app](https://bioreport-ai.streamlit.app)**

Importez un PDF de résultats biologiques, prenez des photos ou collez les valeurs en texte libre → BioReport AI génère en quelques secondes un rapport structuré en 5 sections, téléchargeable en PDF.

---

## Fonctionnalités

### Saisie des résultats
| Mode | Description |
|------|-------------|
| 📄 **PDF** | Extraction automatique du texte via PyMuPDF |
| 📷 **Photo** | Envoi direct d'une ou plusieurs photos au modèle Claude Vision |
| ✏️ **Texte libre** | Copier-coller des valeurs brutes |

### Contexte patient
- Âge, sexe, motif de prescription, antécédents
- **Module transplantation** : type de greffe (cardiaque, rénale, hépatique, pulmonaire, pancréatique…), phase post-greffe, dose et taux résiduel de tacrolimus (C0)

### Traitements
- Saisie manuelle ou **photo d'ordonnance** (extraction automatique par IA)

### Rapport structuré en 5 sections
| # | Section | Description |
|---|---------|-------------|
| 🔴 | **Résumé des anomalies** | Valeurs hors normes classées Légère / Modérée / Critique |
| 🧠 | **Interprétation clinique** | Tableaux cliniques, prise en compte du contexte patient |
| 🔬 | **Diagnostics à évoquer** | Hypothèses du plus au moins probable |
| 📋 | **Recommandations** | Examens complémentaires, délai, avis spécialisé |
| 💊 | **Recommandations posologiques** | Adaptation des doses selon les résultats + néphroprotection chez le transplanté |

### Export
- **Téléchargement PDF** — rapport A4 mis en page avec header, couleurs par section et bloc patient

---

## Démo rapide

```
Hémoglobine : 10.1 g/dL  (N: 13–18)
Leucocytes  : 3.5 G/L    (N: 4–11)
Créatinine  : 147 µmol/L (N: 59–104)
DFG CKD-EPI : 52 mL/min/1,73 m²
NT-proBNP   : 608 ng/L   (N < 125)
CRP         : 7 mg/L     (N < 5)
Tacrolimus C0 : 8.3 ng/mL
```

Patient : Homme 37 ans — Greffe cardiaque — Maintenance précoce (3–12 mois) — Tacrolimus 4 mg/j

→ BioReport AI détecte l'anémie multifactorielle, l'IRC stade 3a, le NT-proBNP élevé, interprète le C0 tacrolimus selon la cible de la phase, et propose une adaptation CNI-sparing avec suivi néphrologue.

---

## Installation locale

### Prérequis
- Python 3.10+
- Clé API Anthropic → [console.anthropic.com](https://console.anthropic.com)

### Étapes

```bash
git clone https://github.com/mamadoulaminetall/BioReport-AI.git
cd BioReport-AI
pip install -r requirements.txt
cp .env.example .env
```

Éditez `.env` :

```
ANTHROPIC_API_KEY=sk-ant-...
```

Lancez :

```bash
streamlit run app.py
```

Ouvrez [http://localhost:8501](http://localhost:8501)

---

## Structure du projet

```
BioReport-AI/
├── app.py            # Interface Streamlit (UI, formulaire, rendu HTML)
├── analyzer.py       # Prompt système + appels Claude API (texte & vision)
├── report_pdf.py     # Génération PDF avec ReportLab
├── pdf_parser.py     # Extraction texte depuis PDF (PyMuPDF)
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| Interface | Streamlit |
| IA | Claude Opus 4.7 (Anthropic API) |
| Vision | Claude Vision — PDF / photos d'ordonnance |
| PDF parsing | PyMuPDF (fitz) |
| Génération PDF | ReportLab |
| Déploiement | Streamlit Cloud |

---

## Déploiement Streamlit Cloud

1. Forkez ce repo
2. Allez sur [share.streamlit.io](https://share.streamlit.io)
3. Connectez votre repo GitHub
4. Dans **Secrets**, ajoutez :
   ```
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
5. Déployez — l'app est en ligne en 2 minutes

---

## Avertissement médical

> Outil d'aide à l'interprétation uniquement. Ne remplace pas le jugement du biologiste médical ou du médecin prescripteur. L'interprétation finale et toute décision thérapeutique restent de la responsabilité exclusive du professionnel de santé.

---

## Auteur

**Dr. Mamadou Lamine TALL** — PhD Bioinformatique  
Fondateur [MedFlow AI](https://github.com/mamadoulaminetall)

---

## Licence

MIT
