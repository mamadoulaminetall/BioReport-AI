import streamlit as st
import os
from dotenv import load_dotenv
from pdf_parser import extract_text
from analyzer import analyze

load_dotenv()

st.set_page_config(
    page_title="BioReport AI",
    page_icon="🧬",
    layout="centered",
)

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stButton>button {
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        border: none;
    }
    .stButton>button:hover { background-color: #1d4ed8; }
    .report-box {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.07);
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧬 BioReport AI")
st.caption("Interprétation automatique de bilan biologique — pour les laboratoires et médecins")

st.divider()

col1, col2 = st.columns([2, 1])

with col1:
    input_mode = st.radio(
        "Mode de saisie",
        ["📄 PDF", "✏️ Texte libre"],
        horizontal=True,
    )

raw_text = ""

if input_mode == "📄 PDF":
    uploaded = st.file_uploader("Importer le compte-rendu PDF", type=["pdf"])
    if uploaded:
        with st.spinner("Extraction du texte..."):
            raw_text = extract_text(uploaded.read())
        st.success(f"{len(raw_text)} caractères extraits")
        with st.expander("Voir le texte extrait"):
            st.text(raw_text[:3000] + ("..." if len(raw_text) > 3000 else ""))
else:
    raw_text = st.text_area(
        "Coller les résultats biologiques ici",
        height=280,
        placeholder="Ex:\nHémoglobine : 9.2 g/dL (N: 12-16)\nLeucocytes : 14.5 G/L (N: 4-10)\nPlaquettes : 420 G/L (N: 150-400)\n...",
    )

st.divider()

api_key = os.environ.get("ANTHROPIC_API_KEY", "")
if not api_key:
    api_key = st.text_input(
        "Clé API Anthropic",
        type="password",
        placeholder="sk-ant-...",
    )
    if api_key:
        os.environ["ANTHROPIC_API_KEY"] = api_key

analyze_btn = st.button("🔍 Analyser le bilan", disabled=not raw_text.strip())

if analyze_btn and raw_text.strip():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        st.error("Clé API Anthropic manquante.")
    else:
        with st.spinner("Analyse en cours..."):
            try:
                report = analyze(raw_text)
                st.divider()
                st.subheader("📋 Rapport d'interprétation")
                st.markdown(f'<div class="report-box">{report}</div>', unsafe_allow_html=True)
                st.download_button(
                    "⬇️ Télécharger le rapport",
                    data=report,
                    file_name="bioreport.txt",
                    mime="text/plain",
                )
            except Exception as e:
                st.error(f"Erreur : {e}")

st.divider()
st.caption("⚠️ Outil d'aide à l'interprétation — ne remplace pas le jugement du biologiste ou du médecin.")
