import streamlit as st
import os
import datetime
from dotenv import load_dotenv
from pdf_parser import extract_text
from analyzer import analyze, analyze_image, extract_treatments
from report_pdf import generate_pdf

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

    input_mode = st.radio("", ["📄 PDF", "📷 Photo", "✏️ Texte libre"], horizontal=True, label_visibility="collapsed")
    raw_text = ""
    image_data = None
    image_media_type = None

    if input_mode == "📄 PDF":
        uploaded = st.file_uploader("", type=["pdf"], label_visibility="collapsed")
        if uploaded:
            with st.spinner("Extraction en cours…"):
                raw_text = extract_text(uploaded.read())
            st.success(f"✓ {len(raw_text)} caractères extraits")
            with st.expander("Aperçu du texte"):
                st.text(raw_text[:2000] + ("…" if len(raw_text) > 2000 else ""))

    elif input_mode == "📷 Photo":
        uploaded_imgs = st.file_uploader(
            "", type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
            accept_multiple_files=True,
        )
        if uploaded_imgs:
            image_data = [(f.read(), f.type if f.type in ("image/jpeg", "image/png", "image/webp") else "image/jpeg") for f in uploaded_imgs]
            cols = st.columns(min(len(image_data), 3))
            for i, (img_bytes, _) in enumerate(image_data):
                cols[i % 3].image(img_bytes, caption=f"Page {i+1}", use_container_width=True)

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

    # ── PATIENT STATUS ────────────────────────────────────────────────────
    st.markdown('<div class="card"><div class="card-label">🧑‍⚕️ Statut du patient</div>', unsafe_allow_html=True)

    pc1, pc2 = st.columns(2)
    with pc1:
        patient_age = st.number_input("Âge (ans)", min_value=0, max_value=120, value=None, placeholder="—", label_visibility="visible")
    with pc2:
        patient_sexe = st.selectbox("Sexe", ["—", "Homme", "Femme", "Autre"], index=0)

    patient_motif = st.text_input(
        "Motif de prescription",
        placeholder="Ex: suivi diabète, bilan pré-opératoire, fatigue…",
    )
    patient_antecedents = st.text_area(
        "Antécédents médicaux",
        height=80,
        placeholder="Ex: HTA, diabète type 2, insuffisance rénale chronique…",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── TREATMENTS ────────────────────────────────────────────────────────
    st.markdown('<div class="card"><div class="card-label">💊 Traitements en cours</div>', unsafe_allow_html=True)

    treat_mode = st.radio("", ["✏️ Saisie manuelle", "📷 Photo ordonnance"], horizontal=True, label_visibility="collapsed", key="treat_mode")

    treatments_text = ""
    treat_image_data = None
    treat_media_type = None

    if treat_mode == "✏️ Saisie manuelle":
        treatments_text = st.text_area(
            "",
            height=90,
            label_visibility="collapsed",
            placeholder="Ex: Metformine 1000mg × 2/j, Ramipril 5mg × 1/j, Atorvastatine 40mg…",
        )
    else:
        treat_img = st.file_uploader("", type=["jpg", "jpeg", "png", "webp"], label_visibility="collapsed", key="treat_upload")
        if treat_img:
            treat_image_data = treat_img.read()
            treat_media_type = treat_img.type if treat_img.type in ("image/jpeg", "image/png", "image/webp") else "image/jpeg"
            st.image(treat_image_data, caption="Ordonnance importée", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    ready = bool(raw_text.strip()) or bool(image_data)
    analyze_btn = st.button("🔍  Analyser le bilan", disabled=not ready)

SECTION_STYLE = {
    "1": ("border-left:4px solid #dc2626", "#fef2f2", "#dc2626"),
    "2": ("border-left:4px solid #2563eb", "#eff6ff", "#2563eb"),
    "3": ("border-left:4px solid #d97706", "#fffbeb", "#d97706"),
    "4": ("border-left:4px solid #16a34a", "#f0fdf4", "#16a34a"),
    "5": ("border-left:4px solid #7c3aed", "#f5f3ff", "#7c3aed"),
}

def _render_report_html(report_text: str, label: str) -> str:
    import re
    ts = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    html = f"""
    <div style="background:white;border-radius:14px;border:1px solid #e2e8f0;
                box-shadow:0 1px 4px rgba(0,0,0,0.05);overflow:hidden;font-family:Inter,sans-serif;">
      <div style="background:linear-gradient(135deg,#1e3a5f,#2563eb);padding:1rem 1.5rem;
                  display:flex;justify-content:space-between;align-items:center;">
        <span style="color:white;font-weight:700;font-size:1rem;">📋 {label}</span>
        <span style="color:rgba(255,255,255,.65);font-size:.78rem;">{ts}</span>
      </div>
      <div style="padding:1.25rem 1.5rem;">
    """
    # Intro block (patient context before first ##)
    intro = re.split(r'(?=## \d)', report_text, maxsplit=1)[0].strip()
    if intro:
        for line in intro.split('\n'):
            line = line.strip()
            if line and line != '---':
                line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
                html += f'<p style="color:#475569;font-size:.88rem;margin:.25rem 0;">{line}</p>'
        html += '<hr style="border:none;border-top:1px solid #e2e8f0;margin:.75rem 0;">'

    sections = re.split(r'(?=## \d)', report_text)
    for section in sections:
        section = section.strip()
        if not section:
            continue
        m = re.match(r'## (\d+)\. (.+)', section)
        if not m:
            continue
        num = m.group(1)
        title = f"{num}. {m.group(2)}"
        border, bg, col = SECTION_STYLE.get(num, ("border-left:4px solid #2563eb", "#eff6ff", "#2563eb"))

        html += f"""
        <div style="{border};background:{bg};border-radius:0 8px 8px 0;
                    padding:.6rem 1rem;margin:.5rem 0 .25rem;">
          <span style="font-weight:700;font-size:.88rem;color:{col};">{title}</span>
        </div>
        <div style="padding:.25rem .5rem .5rem 1.25rem;">
        """
        body = section[m.end():].strip()
        for line in body.split('\n'):
            line = line.strip()
            if not line:
                continue
            line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
            line = re.sub(r'\*(.*?)\*', r'<em>\1</em>', line)
            if line.startswith('- '):
                line = '• ' + line[2:]
            html += f'<p style="font-size:.88rem;color:#1e293b;line-height:1.7;margin:.2rem 0;">{line}</p>'
        html += '</div>'

    html += """
      </div>
      <div style="background:#f8fafc;border-top:1px solid #e2e8f0;padding:.6rem 1.5rem;
                  text-align:center;font-size:.72rem;color:#94a3b8;font-style:italic;">
        ⚠️ Aide à la décision uniquement — ne remplace pas le jugement du médecin prescripteur.
      </div>
    </div>
    """
    return html


with col_right:
    if st.session_state.current_report:
        st.markdown(_render_report_html(
            st.session_state.current_report,
            st.session_state.current_label,
        ), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        pdf_ctx = st.session_state.get("last_patient_ctx")
        pdf_bytes = generate_pdf(
            st.session_state.current_report,
            st.session_state.current_label,
            pdf_ctx,
        )
        st.download_button(
            "⬇️  Télécharger le rapport (PDF)",
            data=pdf_bytes,
            file_name=f"bioreport_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
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
if analyze_btn and (raw_text.strip() or image_data):
    if not os.environ.get("ANTHROPIC_API_KEY"):
        st.error("Clé API Anthropic manquante — ajoutez-la dans la barre latérale.")
    else:
        with st.spinner("Analyse IA en cours…"):
            try:
                # Build patient context dict
                patient_ctx = {}
                if patient_age:
                    patient_ctx["age"] = int(patient_age)
                if patient_sexe and patient_sexe != "—":
                    patient_ctx["sexe"] = patient_sexe
                if patient_motif.strip():
                    patient_ctx["motif"] = patient_motif.strip()
                if patient_antecedents.strip():
                    patient_ctx["antecedents"] = patient_antecedents.strip()
                patient_ctx = patient_ctx or None

                # Extract treatments from photo if needed
                final_treatments = treatments_text.strip() or None
                if treat_image_data:
                    with st.spinner("Extraction des traitements…"):
                        final_treatments = extract_treatments(treat_image_data, treat_media_type)

                if image_data:
                    report = analyze_image(image_data, patient_ctx, final_treatments)
                else:
                    report = analyze(raw_text, patient_ctx, final_treatments)

                ts = datetime.datetime.now().strftime("%H:%M")
                entry_label = label.strip() or f"Bilan {len(st.session_state.history) + 1} · {ts}"
                st.session_state.history.insert(0, {"label": entry_label, "report": report, "raw": raw_text or "📷 image"})
                st.session_state.current_report = report
                st.session_state.current_label = entry_label
                st.session_state.last_patient_ctx = patient_ctx
                st.rerun()
            except Exception as e:
                st.error(f"Erreur : {e}")

st.markdown('<div class="footer">⚠️ Outil d\'aide à l\'interprétation — ne remplace pas le jugement du biologiste médical ou du médecin prescripteur.</div>', unsafe_allow_html=True)
