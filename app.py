import re
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

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 0 !important; padding-bottom: 2rem !important; }

[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"] { background: #f1f5f9; }

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
    color: #94a3b8 !important;
    border: 1px solid #1e293b !important;
    border-radius: 8px !important;
    font-size: 0.81rem !important;
    padding: 0.45rem 0.75rem !important;
    width: 100% !important;
    text-align: left !important;
    transition: all .15s ease !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #2563eb !important;
    border-color: #2563eb !important;
    color: white !important;
}

/* ── NAVBAR ── */
.navbar {
    background: linear-gradient(135deg, #0f2952 0%, #1d4ed8 100%);
    padding: 1.15rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: -1rem -1rem 1.75rem -1rem;
    box-shadow: 0 4px 20px rgba(29,78,216,0.35);
}
.navbar h1 {
    color: white !important; font-size: 1.45rem !important;
    font-weight: 700 !important; margin: 0 !important; letter-spacing: -0.3px !important;
}
.navbar-sub { color: rgba(255,255,255,0.6); font-size: 0.78rem; margin-top: 2px; }
.navbar-badge {
    background: rgba(255,255,255,0.12);
    color: rgba(255,255,255,0.9);
    font-size: 0.68rem; font-weight: 700;
    padding: 5px 14px; border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.2);
    letter-spacing: 0.8px; text-transform: uppercase;
}

/* ── CARDS ── */
.card {
    background: white;
    border-radius: 16px;
    padding: 1.4rem 1.5rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    margin-bottom: 1rem;
    transition: box-shadow .2s ease;
}
.card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.07); }
.card-header {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 1.1rem; padding-bottom: .75rem;
    border-bottom: 1px solid #f1f5f9;
}
.step-num {
    width: 22px; height: 22px;
    background: linear-gradient(135deg,#2563eb,#1d4ed8);
    color: white; border-radius: 50%;
    font-size: 0.68rem; font-weight: 700;
    display: inline-flex; align-items: center; justify-content: center;
    flex-shrink: 0; box-shadow: 0 2px 6px rgba(37,99,235,0.35);
}
.card-label {
    font-size: 0.76rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.8px; color: #475569;
}

/* ── INPUTS ── */
.stTextArea textarea {
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important; font-size: 0.87rem !important;
    background: #f8fafc !important; color: #1e293b !important;
    transition: border-color .15s ease !important;
}
.stTextArea textarea:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
}
.stTextInput > div > input {
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important; font-size: 0.87rem !important;
    background: #f8fafc !important;
    transition: border-color .15s ease !important;
}
.stTextInput > div > input:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
}
[data-testid="stSelectbox"] > div > div,
[data-testid="stNumberInput"] input {
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important; background: #f8fafc !important;
    font-size: 0.87rem !important;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploadDropzone"] {
    border: 2px dashed #cbd5e1 !important;
    border-radius: 12px !important; background: #f8fafc !important;
    transition: all .15s ease !important;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: #2563eb !important; background: #eff6ff !important;
}

/* ── RADIO (pill tabs) ── */
.stRadio > div { flex-direction: row !important; gap: .5rem !important; flex-wrap: wrap !important; }
.stRadio label {
    background: #f1f5f9 !important; border: 1.5px solid #e2e8f0 !important;
    border-radius: 8px !important; padding: .35rem .9rem !important;
    font-size: .83rem !important; font-weight: 500 !important;
    color: #475569 !important; cursor: pointer !important;
    transition: all .15s ease !important;
}
.stRadio label:has(input:checked) {
    background: #eff6ff !important; border-color: #2563eb !important;
    color: #1d4ed8 !important; font-weight: 600 !important;
}

/* ── CHECKBOX ── */
.stCheckbox label { font-size: 0.87rem !important; font-weight: 500 !important; color: #374151 !important; }

/* ── ANALYSE BUTTON ── */
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; padding: 0.65rem 1.5rem !important;
    font-weight: 600 !important; font-size: 0.9rem !important;
    box-shadow: 0 4px 14px rgba(37,99,235,0.3) !important;
    width: 100% !important; transition: all .2s ease !important;
    letter-spacing: 0.2px !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(37,99,235,0.4) !important;
}
.stButton > button:active { transform: translateY(0) !important; }
.stButton > button:disabled {
    background: #e2e8f0 !important; color: #94a3b8 !important;
    box-shadow: none !important; transform: none !important;
}

/* ── DOWNLOAD BUTTON (green) ── */
[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg, #16a34a, #15803d) !important;
    box-shadow: 0 4px 14px rgba(22,163,74,0.28) !important;
}
[data-testid="stDownloadButton"] button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(22,163,74,0.4) !important;
}

/* ── FOOTER ── */
.footer { text-align: center; color: #94a3b8; font-size: 0.75rem; padding: 1.5rem 0 .5rem; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "current_report" not in st.session_state:
    st.session_state.current_report = None
if "current_label" not in st.session_state:
    st.session_state.current_label = ""

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    n = len(st.session_state.history)
    badge = (
        f'<span style="background:#1e3a5f;color:#93c5fd;font-size:.68rem;font-weight:700;'
        f'padding:2px 8px;border-radius:10px;margin-left:6px;">{n}</span>'
        if n else ""
    )
    st.markdown(f"""
        <div style="margin-bottom:1.25rem;display:flex;flex-direction:column;align-items:center;">
          <svg width="190" height="62" viewBox="0 0 220 72" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="hg2" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#7c3aed"/>
                <stop offset="100%" style="stop-color:#2563eb"/>
              </linearGradient>
              <linearGradient id="tg2" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" style="stop-color:#a78bfa"/>
                <stop offset="100%" style="stop-color:#60a5fa"/>
              </linearGradient>
            </defs>
            <path d="M30 18 C30 12 24 8 18 12 C12 16 12 24 18 30 L30 42 L42 30 C48 24 48 16 42 12 C36 8 30 12 30 18Z"
                  fill="url(#hg2)" opacity="0.95"/>
            <polyline points="14,30 19,30 22,22 25,38 28,26 31,30 38,30 41,30"
                      fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" opacity="0.9"/>
            <text x="56" y="32" font-family="'Helvetica Neue',Arial,sans-serif" font-size="22" font-weight="800"
                  fill="url(#tg2)" letter-spacing="-0.5">MedFlow</text>
            <rect x="158" y="16" width="26" height="18" rx="5" fill="url(#hg2)"/>
            <text x="171" y="29" font-family="'Helvetica Neue',Arial,sans-serif" font-size="11" font-weight="700"
                  fill="white" text-anchor="middle" letter-spacing="0.5">AI</text>
            <text x="56" y="52" font-family="'Helvetica Neue',Arial,sans-serif" font-size="11" font-weight="400"
                  fill="#94a3b8" letter-spacing="0.3">BioReport AI · v1.2</text>
          </svg>
        </div>
        <hr style="border-color:#1e293b;margin-bottom:1rem;">
        <div style="font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:0.8px;
                    color:#475569;margin-bottom:.75rem;display:flex;align-items:center;">
            Historique des analyses{badge}
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown('<div style="font-size:.82rem;color:#475569;font-style:italic;">Aucune analyse</div>', unsafe_allow_html=True)
    else:
        for i, entry in enumerate(st.session_state.history):
            if st.button(f"📋 {entry['label']}", key=f"hist_{i}", use_container_width=True):
                st.session_state.current_report = entry["report"]
                st.session_state.current_label = entry["label"]
                st.rerun()

    st.markdown('<hr style="border-color:#1e293b;margin:1rem 0;">', unsafe_allow_html=True)

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        st.markdown('<div style="font-size:.7rem;font-weight:600;text-transform:uppercase;letter-spacing:.8px;color:#475569;margin-bottom:.5rem;">Clé API Anthropic</div>', unsafe_allow_html=True)
        typed_key = st.text_input("", type="password", placeholder="sk-ant-...", label_visibility="collapsed")
        if typed_key:
            os.environ["ANTHROPIC_API_KEY"] = typed_key
            st.rerun()
    else:
        st.markdown('<div style="font-size:.82rem;color:#22c55e;font-weight:600;">✓ API connectée</div>', unsafe_allow_html=True)

# ── NAVBAR ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
    <div style="display:flex;align-items:center;gap:14px;">
        <span style="font-size:1.8rem;filter:drop-shadow(0 2px 4px rgba(0,0,0,0.3));">🧬</span>
        <div>
            <h1>BioReport AI</h1>
            <div class="navbar-sub">Interprétation automatique de bilan biologique</div>
        </div>
    </div>
    <svg width="145" height="48" viewBox="0 0 220 72" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="nhg" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#7c3aed"/>
          <stop offset="100%" style="stop-color:#2563eb"/>
        </linearGradient>
        <linearGradient id="ntg" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" style="stop-color:#c4b5fd"/>
          <stop offset="100%" style="stop-color:#93c5fd"/>
        </linearGradient>
      </defs>
      <path d="M30 18 C30 12 24 8 18 12 C12 16 12 24 18 30 L30 42 L42 30 C48 24 48 16 42 12 C36 8 30 12 30 18Z"
            fill="url(#nhg)" opacity="0.95"/>
      <polyline points="14,30 19,30 22,22 25,38 28,26 31,30 38,30 41,30"
                fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" opacity="0.9"/>
      <text x="56" y="32" font-family="'Helvetica Neue',Arial,sans-serif" font-size="22" font-weight="800"
            fill="url(#ntg)" letter-spacing="-0.5">MedFlow</text>
      <rect x="158" y="16" width="26" height="18" rx="5" fill="url(#nhg)"/>
      <text x="171" y="29" font-family="'Helvetica Neue',Arial,sans-serif" font-size="11" font-weight="700"
            fill="white" text-anchor="middle" letter-spacing="0.5">AI</text>
      <text x="56" y="52" font-family="'Helvetica Neue',Arial,sans-serif" font-size="11" font-weight="400"
            fill="rgba(255,255,255,0.5)" letter-spacing="0.3">Aide à la décision clinique</text>
    </svg>
</div>
""", unsafe_allow_html=True)

# ── COLUMNS ──────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:

    # ── CARD 1 : Saisie ──────────────────────────────────────────────────────
    st.markdown("""
    <div class="card">
      <div class="card-header">
        <span class="step-num">1</span>
        <span class="card-label">Saisie des résultats</span>
      </div>
    """, unsafe_allow_html=True)

    input_mode = st.radio("", ["📄 PDF", "📷 Photo", "✏️ Texte libre"], horizontal=True, label_visibility="collapsed")
    raw_text = ""
    image_data = None

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
            label_visibility="collapsed", accept_multiple_files=True,
        )
        if uploaded_imgs:
            image_data = [
                (f.read(), f.type if f.type in ("image/jpeg", "image/png", "image/webp") else "image/jpeg")
                for f in uploaded_imgs
            ]
            cols = st.columns(min(len(image_data), 3))
            for i, (img_bytes, _) in enumerate(image_data):
                cols[i % 3].image(img_bytes, caption=f"Page {i+1}", use_container_width=True)

    else:
        raw_text = st.text_area(
            "", height=200, label_visibility="collapsed",
            placeholder=(
                "Hémoglobine : 9.2 g/dL   (N: 12–16)\n"
                "Leucocytes  : 14.5 G/L   (N: 4–10)\n"
                "CRP         : 87 mg/L    (N: < 5)\n"
                "Créatinine  : 142 µmol/L (N: 50–100)\n…"
            ),
        )

    label = st.text_input(
        "", placeholder="Étiquette — Ex: Patient A · NFS 01/05/2026",
        label_visibility="collapsed",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── CARD 2 : Patient ─────────────────────────────────────────────────────
    st.markdown("""
    <div class="card">
      <div class="card-header">
        <span class="step-num">2</span>
        <span class="card-label">Statut du patient</span>
      </div>
    """, unsafe_allow_html=True)

    pc1, pc2 = st.columns(2)
    with pc1:
        patient_age = st.number_input("Âge (ans)", min_value=0, max_value=120, value=None, placeholder="—")
    with pc2:
        patient_sexe = st.selectbox("Sexe", ["—", "Homme", "Femme", "Autre"], index=0)

    patient_motif = st.text_input("Motif de prescription", placeholder="Ex: suivi post-greffe, bilan pré-op…")
    patient_antecedents = st.text_area("Antécédents médicaux", height=75,
        placeholder="Ex: HTA, diabète type 2, IRC stade 3…")

    is_transplant = st.checkbox("🏥 Patient transplanté")
    type_greffe = greffe_phase = tacro_dose = tacro_residuel = None

    if is_transplant:
        type_greffe = st.selectbox("Type de greffe", [
            "—", "Greffe cardiaque", "Greffe rénale", "Greffe hépatique",
            "Greffe pulmonaire", "Greffe pancréatique", "Greffe rein–pancréas",
            "Greffe cœur–poumons", "Greffe intestinale", "Multi-organe",
        ], index=0)
        greffe_phase = st.selectbox("Phase post-greffe", [
            "—", "Phase initiale (J0–3 mois)", "Maintenance précoce (3–12 mois)",
            "Maintenance tardive (> 1 an)", "Suspicion de rejet aigu",
            "Suivi long terme (> 5 ans)",
        ], index=0)
        tg1, tg2 = st.columns(2)
        with tg1:
            tacro_dose = st.number_input("Dose tacrolimus (mg/j)", min_value=0.0, max_value=50.0,
                                         value=None, placeholder="—", format="%.1f")
        with tg2:
            tacro_residuel = st.number_input("Résidu tacrolimus (ng/mL)", min_value=0.0, max_value=100.0,
                                              value=None, placeholder="—", format="%.1f")

    st.markdown('</div>', unsafe_allow_html=True)

    # ── CARD 3 : Traitements ─────────────────────────────────────────────────
    st.markdown("""
    <div class="card">
      <div class="card-header">
        <span class="step-num">3</span>
        <span class="card-label">Traitements en cours</span>
      </div>
    """, unsafe_allow_html=True)

    treat_mode = st.radio("", ["✏️ Saisie manuelle", "📷 Photo ordonnance"],
                          horizontal=True, label_visibility="collapsed", key="treat_mode")

    treatments_text = ""
    treat_image_data = None
    treat_media_type = None

    if treat_mode == "✏️ Saisie manuelle":
        treatments_text = st.text_area("", height=85, label_visibility="collapsed",
            placeholder="Ex: Tacrolimus 4mg/j, MMF 1g×2/j, Prédnisolone 5mg/j…")
    else:
        treat_img = st.file_uploader("", type=["jpg", "jpeg", "png", "webp"],
                                     label_visibility="collapsed", key="treat_upload")
        if treat_img:
            treat_image_data = treat_img.read()
            treat_media_type = treat_img.type if treat_img.type in ("image/jpeg", "image/png", "image/webp") else "image/jpeg"
            st.image(treat_image_data, caption="Ordonnance importée", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    ready = bool(raw_text.strip()) or bool(image_data)
    analyze_btn = st.button("🔍  Analyser le bilan", disabled=not ready)


# ── REPORT RENDERER ──────────────────────────────────────────────────────────
SECTION_META = {
    "1": ("#dc2626", "#fef2f2", "🔴"),
    "2": ("#2563eb", "#eff6ff", "🧠"),
    "3": ("#d97706", "#fffbeb", "🔬"),
    "4": ("#16a34a", "#f0fdf4", "📋"),
    "5": ("#7c3aed", "#f5f3ff", "💊"),
}

def _render_report_html(report_text: str, label: str) -> str:
    ts = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    html = f"""
    <div style="background:white;border-radius:16px;border:1px solid #e2e8f0;
                box-shadow:0 2px 8px rgba(0,0,0,0.05);overflow:hidden;font-family:Inter,sans-serif;">
      <div style="background:linear-gradient(135deg,#0f2952,#1d4ed8);padding:1.1rem 1.5rem;
                  display:flex;justify-content:space-between;align-items:center;">
        <div>
          <div style="color:white;font-weight:700;font-size:1rem;letter-spacing:-.2px;">📋 {label}</div>
          <div style="color:rgba(255,255,255,.55);font-size:.74rem;margin-top:2px;">
            Rapport d'interprétation biologique
          </div>
        </div>
        <span style="color:rgba(255,255,255,.7);font-size:.74rem;background:rgba(255,255,255,.1);
                     padding:4px 10px;border-radius:8px;white-space:nowrap;">{ts}</span>
      </div>
      <div style="padding:1.25rem 1.5rem;">
    """

    # Intro (patient context before first ##)
    intro = re.split(r'(?=## \d)', report_text, maxsplit=1)[0].strip()
    if intro:
        html += '<div style="background:#f8fafc;border-radius:10px;padding:.7rem 1rem;margin-bottom:1rem;border:1px solid #e2e8f0;">'
        for line in intro.split('\n'):
            line = line.strip()
            if line and line != '---':
                line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
                html += f'<p style="color:#475569;font-size:.84rem;margin:.18rem 0;line-height:1.6;">{line}</p>'
        html += '</div>'

    # Sections
    for section in re.split(r'(?=## \d)', report_text):
        section = section.strip()
        if not section:
            continue
        m = re.match(r'## (\d+)\. (.+)', section)
        if not m:
            continue
        num, title = m.group(1), m.group(2)
        col, bg, icon = SECTION_META.get(num, ("#2563eb", "#eff6ff", "•"))

        html += f"""
        <div style="margin:.8rem 0 .25rem;">
          <div style="background:{col};border-radius:8px 8px 0 0;padding:.55rem 1rem;
                      display:flex;align-items:center;gap:.55rem;">
            <span style="font-size:.95rem;">{icon}</span>
            <span style="color:white;font-weight:700;font-size:.87rem;letter-spacing:-.1px;">
              {num}. {title}
            </span>
          </div>
          <div style="background:{bg};border-radius:0 0 8px 8px;
                      padding:.7rem 1rem .65rem 1.1rem;border:1px solid {col}22;border-top:none;">
        """

        body = section[m.end():].strip()
        lines = body.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            def fmt(t):
                t = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', t)
                t = re.sub(r'\*(.*?)\*', r'<em>\1</em>', t)
                return t

            is_bullet = line.startswith('- ') or line.startswith('• ')
            if is_bullet:
                html += '<ul style="margin:.15rem 0 .35rem;padding-left:1.15rem;">'
                while i < len(lines) and (lines[i].strip().startswith('- ') or lines[i].strip().startswith('• ')):
                    bl = re.sub(r'^[-•]\s', '', lines[i].strip())
                    html += (f'<li style="font-size:.85rem;color:#1e293b;line-height:1.65;'
                             f'margin:.1rem 0;">{fmt(bl)}</li>')
                    i += 1
                html += '</ul>'
                continue
            elif line.endswith(':') and len(line) < 70 and not line.startswith('•'):
                html += (f'<p style="font-size:.8rem;font-weight:700;color:{col};'
                         f'margin:.5rem 0 .1rem;text-transform:uppercase;letter-spacing:.5px;">'
                         f'{fmt(line)}</p>')
            else:
                html += (f'<p style="font-size:.86rem;color:#1e293b;line-height:1.7;'
                         f'margin:.15rem 0;">{fmt(line)}</p>')
            i += 1

        html += '</div></div>'

    html += """
      </div>
      <div style="background:#f8fafc;border-top:1px solid #e2e8f0;padding:.6rem 1.5rem;
                  text-align:center;font-size:.71rem;color:#94a3b8;font-style:italic;">
        ⚠️ Aide à la décision uniquement — ne remplace pas le jugement du médecin prescripteur
      </div>
    </div>
    """
    return html


# ── RIGHT COLUMN ─────────────────────────────────────────────────────────────
with col_right:
    if st.session_state.current_report:
        st.markdown(
            _render_report_html(st.session_state.current_report, st.session_state.current_label),
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        pdf_bytes = generate_pdf(
            st.session_state.current_report,
            st.session_state.current_label,
            st.session_state.get("last_patient_ctx"),
        )
        st.download_button(
            "⬇️  Télécharger le rapport (PDF)",
            data=pdf_bytes,
            file_name=f"bioreport_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
        )
    else:
        st.markdown("""
        <div style="background:white;border-radius:16px;border:1px solid #e2e8f0;
                    box-shadow:0 2px 8px rgba(0,0,0,0.04);padding:3.5rem 2rem;text-align:center;">
          <div style="font-size:3rem;margin-bottom:1rem;
                      filter:drop-shadow(0 2px 8px rgba(37,99,235,0.2));">🧬</div>
          <div style="font-weight:700;color:#1e293b;font-size:1.05rem;margin-bottom:.5rem;">
            Rapport d'interprétation
          </div>
          <div style="color:#94a3b8;font-size:.84rem;margin-bottom:1.75rem;line-height:1.65;
                      max-width:280px;margin-left:auto;margin-right:auto;">
            Saisissez les résultats biologiques à gauche, renseignez le contexte patient, puis cliquez sur Analyser.
          </div>
          <div style="display:flex;flex-wrap:wrap;gap:.45rem;justify-content:center;">
            <span style="background:#fef2f2;color:#dc2626;padding:5px 12px;border-radius:20px;font-size:.75rem;font-weight:600;">🔴 Anomalies</span>
            <span style="background:#eff6ff;color:#2563eb;padding:5px 12px;border-radius:20px;font-size:.75rem;font-weight:600;">🧠 Interprétation</span>
            <span style="background:#fffbeb;color:#d97706;padding:5px 12px;border-radius:20px;font-size:.75rem;font-weight:600;">🔬 Diagnostics</span>
            <span style="background:#f0fdf4;color:#16a34a;padding:5px 12px;border-radius:20px;font-size:.75rem;font-weight:600;">📋 Recommandations</span>
            <span style="background:#f5f3ff;color:#7c3aed;padding:5px 12px;border-radius:20px;font-size:.75rem;font-weight:600;">💊 Posologie</span>
          </div>
        </div>
        """, unsafe_allow_html=True)


# ── TRIGGER ──────────────────────────────────────────────────────────────────
if analyze_btn and (raw_text.strip() or image_data):
    if not os.environ.get("ANTHROPIC_API_KEY"):
        st.error("Clé API Anthropic manquante — ajoutez-la dans la barre latérale.")
    else:
        with st.spinner("Analyse IA en cours…"):
            try:
                patient_ctx = {}
                if patient_age:
                    patient_ctx["age"] = int(patient_age)
                if patient_sexe and patient_sexe != "—":
                    patient_ctx["sexe"] = patient_sexe
                if patient_motif.strip():
                    patient_ctx["motif"] = patient_motif.strip()
                if patient_antecedents.strip():
                    patient_ctx["antecedents"] = patient_antecedents.strip()
                if is_transplant:
                    patient_ctx["greffe"] = True
                    if type_greffe and type_greffe != "—":
                        patient_ctx["type_greffe"] = type_greffe
                    if greffe_phase and greffe_phase != "—":
                        patient_ctx["phase_greffe"] = greffe_phase
                    if tacro_dose is not None:
                        patient_ctx["tacro_dose"] = tacro_dose
                    if tacro_residuel is not None:
                        patient_ctx["tacro_residuel"] = tacro_residuel
                patient_ctx = patient_ctx or None

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

st.markdown(
    '<div class="footer">⚠️ Outil d\'aide à l\'interprétation — '
    'ne remplace pas le jugement du biologiste médical ou du médecin prescripteur · '
    'BioReport AI v1.2</div>',
    unsafe_allow_html=True,
)
