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
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: #0f172a;
    border-right: none;
}
section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
section[data-testid="stSidebar"] .stButton>button {
    background: #1e293b !important;
    color: #cbd5e1 !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
    text-align: left !important;
    font-size: 0.82rem !important;
    padding: 0.5rem 0.75rem !important;
    margin-bottom: 4px !important;
    width: 100% !important;
}
section[data-testid="stSidebar"] .stButton>button:hover {
    background: #2563eb !important;
    border-color: #2563eb !important;
    color: white !important;
}

/* ── NAVBAR ── */
.navbar {
    background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%);
    padding: 1.1rem 2.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 2px 12px rgba(37,99,235,0.25);
}
.navbar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
}
.navbar-brand h1 {
    color: white !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    margin: 0 !important;
    letter-spacing: -0.3px;
}
.navbar-badge {
    background: rgba(255,255,255,0.15);
    color: white;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.2);
    letter-spacing: 0.5px;
}
.navbar-sub {
    color: rgba(255,255,255,0.7);
    font-size: 0.82rem;
}

/* ── MAIN CONTENT ── */
.main-content {
    padding: 2rem 2.5rem;
    background: #f1f5f9;
    min-height: calc(100vh - 72px);
}

/* ── CARDS ── */
.card {
    background: white;
    border-radius: 14px;
    padding: 1.75rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    margin-bottom: 1.25rem;
}
.card-title {
    font-size: 0.78rem;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 1rem;
}

/* ── INPUT OVERRIDES ── */
.stTextArea textarea {
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important;
    font-family: 'Inter', monospace !important;
    font-size: 0.88rem !important;
    background: #f8fafc !important;
    color: #1e293b !important;
    padding: 0.9rem !important;
}
.stTextArea textarea:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
}
.stTextInput input {
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important;
    font-size: 0.88rem !important;
    background: #f8fafc !important;
}
.stTextInput input:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
    border: 2px dashed #cbd5e1 !important;
    border-radius: 12px !important;
    background: #f8fafc !important;
    padding: 1.5rem !important;
    transition: all 0.2s;
}
[data-testid="stFileUploader"]:hover {
    border-color: #2563eb !important;
    background: #eff6ff !important;
}

/* ── ANALYZE BUTTON ── */
.stButton>button[kind="primary"], div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.65rem 2rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    box-shadow: 0 4px 12px rgba(37,99,235,0.3) !important;
    transition: all 0.2s !important;
    width: 100% !important;
}
.stButton>button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 16px rgba(37,99,235,0.4) !important;
}
.stButton>button:disabled {
    background: #e2e8f0 !important;
    color: #94a3b8 !important;
    box-shadow: none !important;
    transform: none !important;
}

/* ── REPORT ── */
.report-container {
    background: white;
    border-radius: 14px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    overflow: hidden;
}
.report-header {
    background: linear-gradient(135deg, #1e3a5f, #2563eb);
    padding: 1.1rem 1.75rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.report-header h3 {
    color: white !important;
    margin: 0 !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
}
.report-header span {
    color: rgba(255,255,255,0.7);
    font-size: 0.8rem;
}
.report-body {
    padding: 1.75rem;
    line-height: 1.8;
    color: #1e293b;
    font-size: 0.93rem;
}
.report-body h2 {
    color: #1e3a5f !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    margin-top: 1.5rem !important;
    padding-bottom: 6px;
    border-bottom: 2px solid #eff6ff;
}

/* ── RADIO ── */
.stRadio > div {
    flex-direction: row !important;
    gap: 1rem !important;
}
.stRadio label {
    background: #f1f5f9;
    border: 1.5px solid #e2e8f0;
    border-radius: 8px;
    padding: 0.4rem 1rem;
    font-size: 0.88rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s;
}
.stRadio label:has(input:checked) {
    background: #eff6ff;
    border-color: #2563eb;
    color: #2563eb;
}

/* ── DIVIDER ── */
hr { border-color: #e2e8f0 !important; margin: 1.25rem 0 !important; }

/* ── SUCCESS / ERROR ── */
.stSuccess { border-radius: 10px !important; }
.stAlert { border-radius: 10px !important; }

/* ── CAPTION ── */
.caption-footer {
    text-align: center;
    color: #94a3b8;
    font-size: 0.78rem;
    padding: 1.5rem 0 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ──────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "current_report" not in st.session_state:
    st.session_state.current_report = None
if "current_label" not in st.session_state:
    st.session_state.current_label = ""

# ── SIDEBAR ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1.5rem 0 1rem;">
        <div style="font-size:1.3rem;font-weight:700;color:white;">🧬 BioReport AI</div>
        <div style="font-size:0.75rem;color:#64748b;margin-top:4px;">Aide à la décision · v1.0</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div style="font-size:0.72rem;font-weight:600;color:#475569;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:0.75rem;">Historique des analyses</div>', unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown('<div style="font-size:0.82rem;color:#475569;padding:0.5rem 0;">Aucune analyse</div>', unsafe_allow_html=True)
    else:
        for i, entry in enumerate(st.session_state.history):
            if st.button(f"📋 {entry['label']}", key=f"hist_{i}", use_container_width=True):
                st.session_state.current_report = entry["report"]
                st.session_state.current_label = entry["label"]
                st.rerun()

    st.markdown("---")
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        st.markdown('<div style="font-size:0.72rem;font-weight:600;color:#475569;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:0.5rem;">Clé API</div>', unsafe_allow_html=True)
        api_key = st.text_input("", type="password", placeholder="sk-ant-...", label_visibility="collapsed")
        if api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key
    else:
        st.markdown('<div style="font-size:0.78rem;color:#22c55e;">✓ API connectée</div>', unsafe_allow_html=True)

# ── NAVBAR ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
    <div class="navbar-brand">
        <span style="font-size:1.8rem;">🧬</span>
        <div>
            <h1>BioReport AI</h1>
            <div class="navbar-sub">Interprétation automatique de bilan biologique</div>
        </div>
    </div>
    <span class="navbar-badge">AIDE À LA DÉCISION</span>
</div>
""", unsafe_allow_html=True)

# ── MAIN ──────────────────────────────────────────────────────────────────
st.markdown('<div class="main-content">', unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📥 Saisie des résultats</div>', unsafe_allow_html=True)

    input_mode = st.radio("", ["📄 PDF", "✏️ Texte libre"], horizontal=True, label_visibility="collapsed")

    raw_text = ""

    if input_mode == "📄 PDF":
        uploaded = st.file_uploader("", type=["pdf"], label_visibility="collapsed")
        if uploaded:
            with st.spinner("Extraction..."):
                raw_text = extract_text(uploaded.read())
            st.success(f"✓ {len(raw_text)} caractères extraits")
            with st.expander("Aperçu du texte"):
                st.text(raw_text[:2000] + ("..." if len(raw_text) > 2000 else ""))
    else:
        raw_text = st.text_area(
            "",
            height=220,
            label_visibility="collapsed",
            placeholder=(
                "Hémoglobine : 9.2 g/dL   (N: 12–16)\n"
                "Leucocytes  : 14.5 G/L   (N: 4–10)\n"
                "CRP         : 87 mg/L    (N: < 5)\n"
                "Créatinine  : 142 µmol/L (N: 50–100)\n"
                "..."
            ),
        )

    label = st.text_input(
        "",
        placeholder="Étiquette optionnelle — Ex: Patient A · NFS 30/04/2026",
        label_visibility="collapsed",
    )

    st.markdown("</div>", unsafe_allow_html=True)

    analyze_btn = st.button("🔍  Analyser le bilan", disabled=not raw_text.strip())

with col_right:
    if st.session_state.current_report:
        ts_display = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        st.markdown(f"""
        <div class="report-container">
            <div class="report-header">
                <h3>📋 {st.session_state.current_label}</h3>
                <span>{ts_display}</span>
            </div>
            <div class="report-body">{st.session_state.current_report.replace(chr(10), '<br>')}</div>
        </div>
        """, unsafe_allow_html=True)

        st.download_button(
            "⬇️  Télécharger le rapport",
            data=st.session_state.current_report,
            file_name=f"bioreport_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
        )
    else:
        st.markdown("""
        <div style="background:white;border-radius:14px;border:1px solid #e2e8f0;
                    padding:3rem 2rem;text-align:center;height:100%;min-height:320px;
                    display:flex;flex-direction:column;align-items:center;justify-content:center;">
            <div style="font-size:3rem;margin-bottom:1rem;">📊</div>
            <div style="font-weight:600;color:#1e293b;font-size:1rem;margin-bottom:0.5rem;">
                Rapport d'interprétation
            </div>
            <div style="color:#94a3b8;font-size:0.85rem;max-width:280px;line-height:1.6;">
                Importez un PDF ou saisissez les valeurs biologiques, puis cliquez sur Analyser.
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── ANALYZE TRIGGER ───────────────────────────────────────────────────────
if analyze_btn and raw_text.strip():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        st.error("Clé API Anthropic manquante — ajoutez-la dans le panneau gauche.")
    else:
        with st.spinner("Analyse IA en cours…"):
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
                st.rerun()
            except Exception as e:
                st.error(f"Erreur : {e}")

st.markdown("""
<div class="caption-footer">
    ⚠️ Outil d'aide à l'interprétation uniquement — ne remplace pas le jugement du biologiste médical ou du médecin prescripteur.
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
