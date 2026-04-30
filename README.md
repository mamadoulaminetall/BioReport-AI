# 🧬 BioReport AI

**Interprétation automatique de bilan biologique par IA — pour les laboratoires et médecins prescripteurs.**

Uploadez un PDF de résultats biologiques ou collez les valeurs en texte libre → BioReport AI génère en quelques secondes un rapport structuré, clair et exploitable par le clinicien.

---

## Fonctionnalités

- 📄 **Import PDF** — extraction automatique du texte du compte-rendu
- ✏️ **Saisie texte libre** — collez les valeurs directement
- 🔍 **Analyse par IA** (Claude Opus) — rapport en 4 sections :
  1. Résumé des anomalies (avec degré de gravité)
  2. Interprétation clinique
  3. Diagnostics à évoquer
  4. Recommandations
- ⬇️ **Téléchargement** du rapport en `.txt`

---

## Démo rapide

```
Hémoglobine : 9.2 g/dL (N: 12-16)
Leucocytes : 14.5 G/L (N: 4-10)
CRP : 87 mg/L (N: < 5)
```

→ BioReport AI détecte l'anémie modérée + syndrome inflammatoire, propose les diagnostics différentiels et les examens complémentaires.

---

## Installation

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

Éditez `.env` et ajoutez votre clé :

```
ANTHROPIC_API_KEY=sk-ant-...
```

Lancez l'application :

```bash
streamlit run app.py
```

Ouvrez [http://localhost:8501](http://localhost:8501)

---

## Structure du projet

```
BioReport-AI/
├── app.py            # Interface Streamlit
├── analyzer.py       # Prompt système + appel Claude API
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
| IA | Claude Opus (Anthropic API) |
| PDF parsing | PyMuPDF (fitz) |
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

## Avertissement

> Outil d'aide à l'interprétation uniquement. Ne remplace pas le jugement du biologiste médical ou du médecin prescripteur. L'interprétation finale reste de la responsabilité du professionnel de santé.

---

## Auteur

**Dr. Mamadou Lamine TALL** — PhD Bioinformatique  
Fondateur [MedFlow AI](https://github.com/mamadoulaminetall)

---

## Licence

MIT
