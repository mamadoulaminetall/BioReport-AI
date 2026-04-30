import streamlit as st
import os
import datetime
from dotenv import load_dotenv
from pdf_parser import extract_text
from analyzer import analyze

load_dotenv()

st.set_page_config(
    page_title="BioReport AI",
    page_icon="🧬",
    layout="wide",
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
    .stButton>button:disabled { background-color: #94a3b8; }
    .report-box {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.07);
        line-height: 1.7;
    }
    .history-item {
        background: white;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 0.5rem;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history = []
if "current_report" not in st.session_state:
    st.session_state.current_report = None
if "current_label" not in st.session_state:
    st.session_state.current_label = ""

left, right = st.columns([3, 1])

with left:
    st.title("🧬 BioReport AI")
    st.caption("Interprétation automatique de bilan biologique · Aide à la décision clinique")

    st.divider()

    input_mode = st.radio("Mode de saisie", ["📄 PDF", "✏️ Texte libre"], horizontal=True)

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
            height=260,
            placeholder=(
                "Ex:\n"
                "Hémoglobine : 9.2 g/dL  (N: 12–16)\n"
                "Leucocytes : 14.5 G/L   (N: 4–10)\n"
                "CRP : 87 mg/L            (N: < 5)\n"
                "Créatinine : 142 µmol/L (N: 50–100)\n"
                "..."
            ),
        )

    label = st.text_input(
        "Étiquette du bilan (optionnel)",
        placeholder="Ex: Patient A — NFS du 30/04/2026",
    )

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        api_key = st.text_input("Clé API Anthropic", type="password", placeholder="sk-ant-...")
        if api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key

    analyze_btn = st.button("🔍 Analyser le bilan", disabled=not raw_text.strip())

    if analyze_btn and raw_text.strip():
        if not os.environ.get("ANTHROPIC_API_KEY"):
            st.error("Clé API Anthropic manquante.")
        else:
            with st.spinner("Analyse IA en cours..."):
                try:
                    report = analyze(raw_text)
                    ts = datetime.datetime.now().strftime("%H:%M")
                    entry_label = label.strip() or f"Bilan {len(st.session_state.history) + 1} · {ts}"
                    st.session_state.history.insert(0, {
                        "label": entry_label,
                        "report": report,
                        "raw": raw_text,
                    })
                    st.session_state.current_report = report
                    st.session_state.current_label = entry_label
                except Exception as e:
                    st.error(f"Erreur : {e}")

    if st.session_state.current_report:
        st.divider()
        st.subheader(f"📋 {st.session_state.current_label}")
        st.markdown(
            f'<div class="report-box">{st.session_state.current_report}</div>',
            unsafe_allow_html=True,
        )
        st.download_button(
            "⬇️ Télécharger le rapport (.txt)",
            data=st.session_state.current_report,
            file_name=f"bioreport_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
        )

    st.divider()
    st.caption("⚠️ Outil d'aide à l'interprétation — ne remplace pas le jugement du biologiste ou du médecin.")

with right:
    st.markdown("### 🗂 Historique")
    if not st.session_state.history:
        st.caption("Aucune analyse pour le moment.")
    else:
        for i, entry in enumerate(st.session_state.history):
            if st.button(entry["label"], key=f"hist_{i}", use_container_width=True):
                st.session_state.current_report = entry["report"]
                st.session_state.current_label = entry["label"]
                st.rerun()
