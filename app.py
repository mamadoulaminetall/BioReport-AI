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

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer { visibility: hidden; }

/* Remove default top padding */
.block-container { padding-top: 0 !important; padding-bottom: 2rem !important; }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] > div:first-child {
    background: #0f172a;
    padding: 1.5rem 1rem;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div { color: #cbd5e1 !important; }

section[data-testid="stSidebar"] .stButton > button {
    background: #1e293b !important;
    color: #cbd5e1 !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    padding: 0.5rem 0.75rem !important;
    width: 100% !important;
    text-align: left !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #2563eb !important;
    border-color: #2563eb !important;
    color: white !important;
}

/* ── NAVBAR ── */
.navbar {
    background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%);
    padding: 1.1rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: -1rem -1rem 2rem -1rem;
    box-shadow: 0 2px 16px rgba(37,99,235,0.3);
}
.navbar h1 { color: white !important; font-size: 1.45rem !important; font-weight: 700 !important; margin: 0 !important; }
.navbar-sub { color: rgba(255,255,255,0.65); font-size: 0.8rem; margin-top: 2px; }
.navbar-badge {
    background: rgba(255,255,255,0.15);
    color: white;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.25);
    letter-spacing: 0.5px;
}

/* ── CARDS ── */
.card {
    background: white;
    border-radius: 14px;
    padding: 1.5rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    margin-bottom: 1rem;
}
.card-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #64748b;
    margin-bottom: 1rem;
}

/* ── INPUTS ── */
.stTextArea textarea {
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important;
    font-size: 0.87rem !important;
    background: #f8fafc !important;
    color: #1e293b !important;
}
.stTextArea textarea:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
}
.stTextInput > div > input {
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important;
    font-size: 0.87rem !important;
    background: #f8fafc !important;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploadDropzone"] {
    border: 2px dashed #cbd5e1 !important;
    border-radius: 12px !important;
    background: #f8fafc !important;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: #2563eb !important;
    background: #eff6ff !important;
}

/* ── RADIO ── */
.stRadio > div { flex-direction: row !important; gap: 0.75rem !important; }

/* ── BUTTON ── */
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.65rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    box-shadow: 0 4px 12px rgba(37,99,235,0.28) !important;
    width: 100% !important;
}
.stButton > button:hover { box-shadow: 0 6px 18px rgba(37,99,235,0.4) !important; }
.stButton > button:disabled {
    background: #e2e8f0 !important;
    color: #94a3b8 !important;
    box-shadow: none !important;
}

/* ── REPORT ── */
.report-wrap {
    background: white;
    border-radius: 14px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    overflow: hidden;
}
.report-head {
    background: linear-gradient(135deg, #1e3a5f, #2563eb);
    padding: 1rem 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.report-head-title { color: white !important; font-size: 0.95rem; font-weight: 600; }
.report-head-date  { color: rgba(255,255,255,0.65); font-size: 0.78rem; }
.report-body {
    padding: 1.5rem;
    line-height: 1.85;
    color: #1e293b;
    font-size: 0.91rem;
}
.report-body h2 {
    font-size: 0.92rem !important;
    font-weight: 700 !important;
    color: #1e3a5f !important;
    border-bottom: 2px solid #eff6ff;
    padding-bottom: 5px;
    margin-top: 1.25rem !important;
}

/* ── EMPTY STATE ── */
.empty-state {
    background: white;
    border-radius: 14px;
    border: 1px solid #e2e8f0;
    padding: 4rem 2rem;
    text-align: center;
}
.empty-icon { font-size: 2.8rem; margin-bottom: 1rem; }
.empty-title { font-weight: 600; color: #1e293b; font-size: 1rem; margin-bottom: 0.4rem; }
.empty-sub { color: #94a3b8; font-size: 0.84rem; line-height: 1.6; max-width: 260px; margin: 0 auto; }

/* ── FOOTER ── */
.footer { text-align: center; color: #94a3b8; font-size: 0.76rem; padding-top: 1.5rem; }

/* Page background */
[data-testid="stAppViewContainer"] { background: #f1f5f9; }
[data-testid="stAppViewBlockContainer"] { background: #f1f5f9; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "current_report" not in st.session_state:
    st.session_state.current_report = None
if "current_label" not in st.session_state:
    st.session_state.current_label = ""

# ── SIDEBAR ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div style="margin-bottom:1.5rem;">
            <div style="font-size:1.2rem;font-weight:700;color:white;">🧬 BioReport AI</div>
            <div style="font-size:0.73rem;color:#475569;margin-top:3px;">Aide à la décision · v1.0</div>
        </div>
        <hr style="border-color:#1e293b;margin-bottom:1rem;">
        <div style="font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:0.8px;color:#475569;margin-bottom:0.75rem;">
            Historique des analyses
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown('<div style="font-size:0.82rem;color:#475569;">Aucune analyse</div>', unsafe_allow_html=True)
    else:
        for i, entry in enumerate(st.session_state.history):
            if st.button(f"📋 {entry['label']}", key=f"hist_{i}", use_container_width=True):
                st.session_state.current_report = entry["report"]
                st.session_state.current_label = entry["label"]
                st.rerun()

    st.markdown('<hr style="border-color:#1e293b;margin:1rem 0;">', unsafe_allow_html=True)

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        st.markdown('<div style="font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:0.8px;color:#475569;margin-bottom:0.5rem;">Clé API Anthropic</div>', unsafe_allow_html=True)
        typed_key = st.text_input("", type="password", placeholder="sk-ant-...", label_visibility="collapsed")
        if typed_key:
            os.environ["ANTHROPIC_API_KEY"] = typed_key
            st.rerun()
    else:
        st.markdown('<div style="font-size:0.82rem;color:#22c55e;font-weight:500;">✓ API connectée</div>', unsafe_allow_html=True)

# ── NAVBAR ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
    <div style="display:flex;align-items:center;gap:12px;">
        <span style="font-size:1.7rem;">🧬</span>
        <div>
            <h1>BioReport AI</h1>
            <div class="navbar-sub">Interprétation automatique de bilan biologique</div>
        </div>
    </div>
    <span class="navbar-badge">AIDE À LA DÉCISION</span>
</div>
""", unsafe_allow_html=True)

# ── COLUMNS ──────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown('<div class="card"><div class="card-label">📥 Saisie des résultats</div>', unsafe_allow_html=True)

    input_mode = st.radio("", ["📄 PDF", "✏️ Texte libre"], horizontal=True, label_visibility="collapsed")
    raw_text = ""

    if input_mode == "📄 PDF":
        uploaded = st.file_uploader("", type=["pdf"], label_visibility="collapsed")
        if uploaded:
            with st.spinner("Extraction en cours…"):
                raw_text = extract_text(uploaded.read())
            st.success(f"✓ {len(raw_text)} caractères extraits")
            with st.expander("Aperçu du texte"):
                st.text(raw_text[:2000] + ("…" if len(raw_text) > 2000 else ""))
    else:
        raw_text = st.text_area(
            "",
            height=210,
            label_visibility="collapsed",
            placeholder=(
                "Hémoglobine : 9.2 g/dL   (N: 12–16)\n"
                "Leucocytes  : 14.5 G/L   (N: 4–10)\n"
                "CRP         : 87 mg/L    (N: < 5)\n"
                "Créatinine  : 142 µmol/L (N: 50–100)\n"
                "…"
            ),
        )

    label = st.text_input(
        "",
        placeholder="Étiquette — Ex: Patient A · NFS 30/04/2026",
        label_visibility="collapsed",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    analyze_btn = st.button("🔍  Analyser le bilan", disabled=not raw_text.strip())

with col_right:
    if st.session_state.current_report:
        ts_display = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        report_html = st.session_state.current_report.replace("\n", "<br>")
        st.markdown(f"""
        <div class="report-wrap">
            <div class="report-head">
                <span class="report-head-title">📋 {st.session_state.current_label}</span>
                <span class="report-head-date">{ts_display}</span>
            </div>
            <div class="report-body">{report_html}</div>
        </div>
        """, unsafe_allow_html=True)

        st.download_button(
            "⬇️  Télécharger le rapport (.txt)",
            data=st.session_state.current_report,
            file_name=f"bioreport_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
        )
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📊</div>
            <div class="empty-title">Rapport d'interprétation</div>
            <div class="empty-sub">
                Importez un PDF ou saisissez les valeurs biologiques, puis cliquez sur Analyser.
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── TRIGGER ──────────────────────────────────────────────────────────────
if analyze_btn and raw_text.strip():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        st.error("Clé API Anthropic manquante — ajoutez-la dans la barre latérale.")
    else:
        with st.spinner("Analyse IA en cours…"):
            try:
                report = analyze(raw_text)
                ts = datetime.datetime.now().strftime("%H:%M")
                entry_label = label.strip() or f"Bilan {len(st.session_state.history) + 1} · {ts}"
                st.session_state.history.insert(0, {"label": entry_label, "report": report, "raw": raw_text})
                st.session_state.current_report = report
                st.session_state.current_label = entry_label
                st.rerun()
            except Exception as e:
                st.error(f"Erreur : {e}")

st.markdown('<div class="footer">⚠️ Outil d\'aide à l\'interprétation — ne remplace pas le jugement du biologiste médical ou du médecin prescripteur.</div>', unsafe_allow_html=True)
