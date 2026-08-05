import re
from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable, SimpleDocTemplate, Spacer, Table, TableStyle, Paragraph, KeepTogether
)

W = 17 * cm
PAGE_W, PAGE_H = A4

# Palette Power BI - MedFlow
C = {
    "navy":    "#0f2952",
    "blue":    "#2563eb",
    "blue_lt": "#dbeafe",
    "red":     "#dc2626",
    "red_lt":  "#fef2f2",
    "amber":   "#d97706",
    "amber_lt":"#fffbeb",
    "green":   "#16a34a",
    "green_lt":"#f0fdf4",
    "purple":  "#7c3aed",
    "purple_lt":"#f5f3ff",
    "slate":   "#475569",
    "slate_lt":"#f8fafc",
    "border":  "#e2e8f0",
    "text":    "#1e293b",
    "muted":   "#94a3b8",
    "white":   "#ffffff",
    "yellow":  "#eab308",
    "orange":  "#f97316",
}

SECTION_META = {
    "1": (C["red"],    C["red_lt"],    "Résumé des anomalies"),
    "2": (C["blue"],   C["blue_lt"],   "Interprétation clinique"),
    "3": (C["amber"],  C["amber_lt"],  "Diagnostics différentiels"),
    "4": (C["green"],  C["green_lt"],  "Recommandations cliniques"),
    "5": (C["purple"], C["purple_lt"], "Recommandations posologiques"),
}


def _c(hex_color: str) -> colors.HexColor:
    return colors.HexColor(hex_color)


def _p(text: str, style: ParagraphStyle) -> Paragraph:
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    text = (text
        .replace('🟡', '<font color="#eab308">[!]</font>')
        .replace('🟠', '<font color="#f97316">[!!]</font>')
        .replace('🔴', '<font color="#dc2626">[!!!]</font>')
        .replace('✅', '<font color="#16a34a">[OK]</font>')
        .replace('⚠️', '<font color="#d97706">[!]</font>')
        .replace('⚠', '<font color="#d97706">[!]</font>')
        .replace('🧬', '')
        .replace('🔬', '')
        .replace('📋', '')
        .replace('💊', '')
        .replace('🧠', '')
        .replace('→', '->')
        .replace('↑', '[+]')
        .replace('↓', '[-]')
        .replace('≥', '>=')
        .replace('≤', '<=')
        .replace('°', 'deg')
    )
    return Paragraph(text, style)


def _count_anomalies(report_text: str):
    """Extract anomaly counts from section 1 for the dashboard."""
    critical = moderate = mild = 0
    section1 = ""
    parts = re.split(r'(?=## \d)', report_text)
    for part in parts:
        if re.match(r'## 1\.', part):
            section1 = part
            break
    critical = len(re.findall(r'CRITIQUE|🔴', section1))
    moderate = len(re.findall(r'MODÉRÉE|MODEREE|🟠', section1))
    mild = len(re.findall(r'LÉGÈRE|LEGERE|🟡', section1))
    return critical, moderate, mild


def generate_pdf(report_text: str, label: str, patient_ctx: dict | None = None) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        rightMargin=1.8 * cm, leftMargin=1.8 * cm,
        topMargin=1.6 * cm, bottomMargin=1.8 * cm,
        title="BioReport AI — Rapport d'interprétation biologique",
    )

    # ── Styles ──────────────────────────────────────────────────────────
    def ps(name, **kw) -> ParagraphStyle:
        base = dict(fontName="Helvetica", fontSize=9, textColor=_c(C["text"]),
                    leading=14, spaceAfter=2)
        base.update(kw)
        return ParagraphStyle(name, **base)

    s_body    = ps("body",   alignment=TA_JUSTIFY, leading=14.5, fontSize=8.8)
    s_small   = ps("small",  fontSize=7.5, textColor=_c(C["slate"]))
    s_disc    = ps("disc",   fontSize=7, textColor=_c(C["muted"]), alignment=TA_CENTER, fontName="Helvetica-Oblique")
    s_intro   = ps("intro",  fontSize=8.8, textColor=_c(C["slate"]), alignment=TA_JUSTIFY, leading=14)
    s_val     = ps("val",    fontSize=8.8, textColor=_c(C["text"]))
    s_lbl     = ps("lbl",    fontSize=7, fontName="Helvetica-Bold", textColor=_c(C["slate"]), spaceAfter=1)
    s_kpi_num = ps("kpi_n",  fontSize=18, fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=0)
    s_kpi_lbl = ps("kpi_l",  fontSize=7, textColor=_c(C["slate"]), alignment=TA_CENTER, spaceAfter=0)

    story = []

    # ── HEADER BANNER ───────────────────────────────────────────────────
    hdr_left = Table([[
        _p("BioReport AI", ps("ht", fontSize=20, fontName="Helvetica-Bold",
                               textColor=colors.white, spaceAfter=0, leading=22)),
        _p(f"Genere le {datetime.now().strftime('%d/%m/%Y a %H:%M')}",
           ps("hd", fontSize=8, textColor=_c("#93c5fd"), alignment=TA_RIGHT, spaceAfter=0)),
    ]], colWidths=[9.5 * cm, 7.5 * cm])
    hdr_left.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _c(C["navy"])),
        ("TOPPADDING",    (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (0, -1), 16),
        ("RIGHTPADDING",  (-1, 0), (-1, -1), 16),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",  (1, 0), (1, -1), "RIGHT"),
    ]))
    story.append(hdr_left)

    # Subtitle bar
    sub_bar = Table([[
        _p("Rapport d'interpretation biologique — Aide a la decision clinique",
           ps("sb", fontSize=8, textColor=_c("#60a5fa"), spaceAfter=0)),
        _p("MedFlow AI · medflow-ai.fr",
           ps("sb2", fontSize=8, textColor=_c("#334155"), alignment=TA_RIGHT, spaceAfter=0)),
    ]], colWidths=[10 * cm, 7 * cm])
    sub_bar.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _c("#0a1628")),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 16),
        ("RIGHTPADDING",  (-1, 0), (-1, -1), 16),
    ]))
    story.append(sub_bar)
    story.append(Spacer(1, 0.35 * cm))

    # Label
    story.append(_p(f"<b>{label}</b>",
                    ps("lbl2", fontSize=11, fontName="Helvetica-Bold",
                       textColor=_c(C["blue"]), spaceAfter=6)))

    # ── PATIENT BOX ─────────────────────────────────────────────────────
    if patient_ctx:
        rows = []
        age = f"{patient_ctx['age']} ans" if patient_ctx.get("age") else None
        sex = patient_ctx.get("sexe") if patient_ctx.get("sexe") not in (None, "—") else None
        if age or sex:
            rows.append([
                _p("AGE", s_lbl), _p(age or "—", s_val),
                _p("SEXE", s_lbl), _p(sex or "—", s_val),
            ])
        if patient_ctx.get("motif"):
            rows.append([
                _p("MOTIF", s_lbl), _p(patient_ctx["motif"], s_val),
                _p("", s_lbl), _p("", s_val),
            ])
        if patient_ctx.get("antecedents"):
            rows.append([
                _p("ATCD", s_lbl), _p(patient_ctx["antecedents"], s_val),
                _p("", s_lbl), _p("", s_val),
            ])
        if patient_ctx.get("greffe"):
            gtype = patient_ctx.get("type_greffe", "Transplantation")
            gphase = patient_ctx.get("phase_greffe", "")
            rows.append([
                _p("TRANSPLANT.", s_lbl), _p(gtype, s_val),
                _p("PHASE", s_lbl), _p(gphase or "—", s_val),
            ])
            tacro_parts = []
            if patient_ctx.get("tacro_dose") is not None:
                tacro_parts.append(f"Dose: {patient_ctx['tacro_dose']} mg/j")
            if patient_ctx.get("tacro_residuel") is not None:
                tacro_parts.append(f"C0: {patient_ctx['tacro_residuel']} ng/mL")
            if tacro_parts:
                rows.append([
                    _p("TACROLIMUS", s_lbl), _p("   |   ".join(tacro_parts), s_val),
                    _p("", s_lbl), _p("", s_val),
                ])
        if rows:
            pt = Table(rows, colWidths=[2.8 * cm, 5.7 * cm, 2.8 * cm, 5.7 * cm])
            pt.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), _c(C["slate_lt"])),
                ("BOX", (0, 0), (-1, -1), 0.5, _c(C["border"])),
                ("TOPPADDING",    (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING",   (0, 0), (-1, -1), 8),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
            ]))
            story.append(pt)
            story.append(Spacer(1, 0.35 * cm))

    # ── KPI DASHBOARD (Power BI style) ───────────────────────────────────
    critical, moderate, mild = _count_anomalies(report_text)
    total_anom = critical + moderate + mild

    kpi_c_bg = _c(C["red_lt"]) if critical > 0 else _c(C["slate_lt"])
    kpi_c_fg = _c(C["red"])    if critical > 0 else _c(C["muted"])
    kpi_m_bg = _c(C["amber_lt"]) if moderate > 0 else _c(C["slate_lt"])
    kpi_m_fg = _c(C["amber"])    if moderate > 0 else _c(C["muted"])
    kpi_ok_bg = _c(C["green_lt"])
    kpi_ok_fg = _c(C["green"])

    kpi_row = Table([[
        Table([[
            _p(str(critical), ps(f"kn1", fontSize=22, fontName="Helvetica-Bold",
                                  alignment=TA_CENTER, textColor=kpi_c_fg, spaceAfter=2)),
            _p("VALEURS CRITIQUES", ps(f"kl1", fontSize=6.5, fontName="Helvetica-Bold",
                                        alignment=TA_CENTER, textColor=_c(C["slate"]),
                                        spaceAfter=0, letterSpacing=0.5)),
        ]], colWidths=[3.5 * cm]),

        Table([[
            _p(str(moderate), ps(f"kn2", fontSize=22, fontName="Helvetica-Bold",
                                   alignment=TA_CENTER, textColor=kpi_m_fg, spaceAfter=2)),
            _p("ANOMALIES MODEREES", ps(f"kl2", fontSize=6.5, fontName="Helvetica-Bold",
                                         alignment=TA_CENTER, textColor=_c(C["slate"]),
                                         spaceAfter=0)),
        ]], colWidths=[3.5 * cm]),

        Table([[
            _p(str(mild), ps(f"kn3", fontSize=22, fontName="Helvetica-Bold",
                              alignment=TA_CENTER, textColor=_c(C["yellow"]), spaceAfter=2)),
            _p("ANOMALIES LEGERES", ps(f"kl3", fontSize=6.5, fontName="Helvetica-Bold",
                                        alignment=TA_CENTER, textColor=_c(C["slate"]),
                                        spaceAfter=0)),
        ]], colWidths=[3.5 * cm]),

        Table([[
            _p(str(total_anom), ps(f"kn4", fontSize=22, fontName="Helvetica-Bold",
                                    alignment=TA_CENTER, textColor=_c(C["blue"]), spaceAfter=2)),
            _p("TOTAL ANOMALIES", ps(f"kl4", fontSize=6.5, fontName="Helvetica-Bold",
                                      alignment=TA_CENTER, textColor=_c(C["slate"]),
                                      spaceAfter=0)),
        ]], colWidths=[3.5 * cm]),

        Table([[
            _p("5", ps(f"kn5", fontSize=22, fontName="Helvetica-Bold",
                        alignment=TA_CENTER, textColor=_c(C["blue"]), spaceAfter=2)),
            _p("SECTIONS RAPPORT", ps(f"kl5", fontSize=6.5, fontName="Helvetica-Bold",
                                       alignment=TA_CENTER, textColor=_c(C["slate"]),
                                       spaceAfter=0)),
        ]], colWidths=[2.5 * cm]),
    ]], colWidths=[3.5 * cm, 3.5 * cm, 3.5 * cm, 3.5 * cm, 2.5 * cm])

    # style each inner table
    for i, (tbl, bg, border_c) in enumerate([
        (kpi_row._cellvalues[0][0], kpi_c_bg, kpi_c_fg),
        (kpi_row._cellvalues[0][1], kpi_m_bg, kpi_m_fg),
        (kpi_row._cellvalues[0][2], _c(C["slate_lt"]), _c(C["yellow"])),
        (kpi_row._cellvalues[0][3], _c(C["blue_lt"]), _c(C["blue"])),
        (kpi_row._cellvalues[0][4], _c(C["slate_lt"]), _c(C["blue"])),
    ]):
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), bg),
            ("TOPPADDING",    (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING",   (0, 0), (-1, -1), 4),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
            ("BOX", (0, 0), (-1, -1), 1.2, border_c),
        ]))

    kpi_row.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING",   (0, 0), (-1, -1), 3),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 3),
    ]))

    story.append(KeepTogether([
        _p("TABLEAU DE BORD", ps("db_ttl", fontSize=7, fontName="Helvetica-Bold",
                                   textColor=_c(C["slate"]), spaceAfter=5,
                                   letterSpacing=1)),
        kpi_row,
        Spacer(1, 0.4 * cm),
    ]))

    # ── INTRO (patient context before first ##) ─────────────────────────
    intro_split = re.split(r'(?=## \d)', report_text, maxsplit=1)
    if intro_split[0].strip():
        intro_items = []
        for line in intro_split[0].strip().split('\n'):
            line = line.strip()
            if line and line != '---':
                intro_items.append(_p(line, s_intro))
        if intro_items:
            intro_tbl = Table([[ip] for ip in intro_items], colWidths=[W])
            intro_tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), _c(C["slate_lt"])),
                ("BOX",        (0, 0), (-1, -1), 0.5, _c(C["border"])),
                ("TOPPADDING",    (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING",   (0, 0), (-1, -1), 12),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
            ]))
            story.append(intro_tbl)
            story.append(Spacer(1, 0.3 * cm))

    # ── SECTIONS ────────────────────────────────────────────────────────
    sections = re.split(r'(?=## \d)', report_text)
    for section in sections:
        section = section.strip()
        if not section:
            continue
        m = re.match(r'## (\d+)\. (.+)', section)
        if not m:
            continue

        num = m.group(1)
        col_h, col_bg, _ = SECTION_META.get(num, (C["blue"], C["blue_lt"], ""))

        # Section header with left accent
        sec_hdr = Table([[
            Table([[Spacer(1, 1)]], colWidths=[0.3 * cm]),
            _p(f"{num}. {m.group(2)}", ps(f"sh{num}", fontSize=10.5, fontName="Helvetica-Bold",
                                           textColor=colors.white, spaceAfter=0)),
        ]], colWidths=[0.4 * cm, W - 0.4 * cm])
        sec_hdr.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), _c(col_h)),
            ("BACKGROUND",    (0, 0), (0, -1), _c("#ffffff33")),
            ("TOPPADDING",    (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
            ("LEFTPADDING",   (1, 0), (1, -1), 12),
        ]))

        body_lines = section[m.end():].strip().split('\n')
        body_paras = []
        i = 0
        while i < len(body_lines):
            line = body_lines[i].strip()
            if not line:
                body_paras.append(Spacer(1, 0.12 * cm))
                i += 1
                continue

            is_bullet = line.startswith('- ') or line.startswith('• ')
            is_sub_title = line.endswith(':') and len(line) < 80 and not is_bullet

            if is_bullet:
                bullet_text = re.sub(r'^[-•]\s', '• ', line)
                body_paras.append(_p(bullet_text, ps(f"bl{num}", fontSize=8.6,
                                                      alignment=TA_LEFT, leading=14,
                                                      leftIndent=8)))
            elif is_sub_title:
                body_paras.append(_p(line, ps(f"st{num}", fontSize=8, fontName="Helvetica-Bold",
                                               textColor=_c(col_h), spaceAfter=2, spaceBefore=4)))
            else:
                body_paras.append(_p(line, s_body))
            i += 1

        if body_paras:
            body_rows = [[bp] for bp in body_paras]
            body_tbl = Table(body_rows, colWidths=[W])
            body_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), _c(col_bg)),
                ("BOX",           (0, 0), (-1, -1), 0.5, _c(col_h + "40")),
                ("TOPPADDING",    (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING",   (0, 0), (-1, -1), 14),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
            ]))
            story.append(KeepTogether([sec_hdr, body_tbl]))
        else:
            story.append(sec_hdr)

        story.append(Spacer(1, 0.3 * cm))

    # ── SCIENTIFIC REFERENCES FOOTNOTE ───────────────────────────────────
    story.append(Spacer(1, 0.2 * cm))
    ref_hdr = Table([[
        _p("REFERENCES SCIENTIFIQUES (algorithme BioReport AI)",
           ps("rh", fontSize=7, fontName="Helvetica-Bold", textColor=_c(C["slate"]),
              spaceAfter=0)),
    ]], colWidths=[W])
    ref_hdr.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), _c(C["slate_lt"])),
        ("BOX",           (0, 0), (-1, -1), 0.4, _c(C["border"])),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
    ]))
    story.append(ref_hdr)

    refs = [
        "[1] Inker LA, et al. CKD-EPI 2021 Equation. N Engl J Med. 2021;385:1737.",
        "[2] Friedewald WT, et al. LDL estimation. Clin Chem. 1972;18:499.",
        "[3] Thygesen K, et al. 4th Universal Definition of MI. Circulation. 2018;138:e618.",
        "[4] Ponikowski P, et al. ESC Heart Failure Guidelines 2016. Eur Heart J. 2016;37:2129.",
        "[5] KDIGO CKD Work Group. Kidney Int Suppl. 2013;3:1.",
        "[6] CLSI EP28-A3c. Reference Intervals. 2010. | [7] Ridker PM. hs-CRP. JACC. 2016;67:712.",
    ]
    refs_paras = [_p(r, ps(f"rf{i}", fontSize=6.8, textColor=_c(C["muted"]), spaceAfter=1)) for i, r in enumerate(refs)]
    refs_tbl = Table([[rp] for rp in refs_paras], colWidths=[W])
    refs_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _c(C["slate_lt"])),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("BOX",           (0, 0), (-1, -1), 0.4, _c(C["border"])),
        ("LINEABOVE",     (0, 0), (-1, 0), 0, colors.white),
    ]))
    story.append(refs_tbl)

    # ── FOOTER ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.25 * cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=_c(C["border"])))
    story.append(Spacer(1, 0.15 * cm))
    story.append(_p(
        "[!] Document d'aide a l'interpretation uniquement. "
        "Ne remplace pas le jugement du biologiste medical ou du medecin prescripteur. "
        "BioReport AI v2.0 — MedFlow AI · medflow-ai.fr",
        s_disc
    ))

    doc.build(story)
    return buf.getvalue()
