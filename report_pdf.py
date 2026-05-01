import re
from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable, SimpleDocTemplate, Spacer, Table, TableStyle, Paragraph
)

W = 17 * cm

SECTION_COLOR = {
    "1": ("#dc2626", "#fef2f2"),
    "2": ("#2563eb", "#eff6ff"),
    "3": ("#d97706", "#fffbeb"),
    "4": ("#16a34a", "#f0fdf4"),
    "5": ("#7c3aed", "#f5f3ff"),
}

def _c(hex_color: str) -> colors.HexColor:
    return colors.HexColor(hex_color)

def _p(text: str, style: ParagraphStyle) -> Paragraph:
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    # Replace emoji with text labels for reportlab
    text = (text
        .replace('🟡', '[Légère]')
        .replace('🟠', '[Modérée]')
        .replace('🔴', '[Critique]')
        .replace('✅', '[OK]')
        .replace('⚠️', '[!]')
        .replace('⚠', '[!]')
        .replace('🧬', '')
    )
    return Paragraph(text, style)


def generate_pdf(report_text: str, label: str, patient_ctx: dict | None = None) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title="BioReport AI — Rapport d'interprétation",
    )

    # ── Styles ──────────────────────────────────────────────────────────
    def ps(name, **kw) -> ParagraphStyle:
        base = dict(fontName="Helvetica", fontSize=9.5, textColor=_c("#1e293b"),
                    leading=14, spaceAfter=3)
        base.update(kw)
        return ParagraphStyle(name, **base)

    s_body      = ps("body", alignment=TA_JUSTIFY, leading=15)
    s_small     = ps("small", fontSize=8, textColor=_c("#64748b"))
    s_label     = ps("label", fontSize=7.5, fontName="Helvetica-Bold",
                     textColor=_c("#64748b"), spaceAfter=1)
    s_val       = ps("val", fontSize=9, textColor=_c("#1e293b"))
    s_disc      = ps("disc", fontSize=7.5, textColor=_c("#94a3b8"),
                     alignment=TA_CENTER, fontName="Helvetica-Oblique")
    s_intro     = ps("intro", fontSize=9, textColor=_c("#475569"),
                     alignment=TA_JUSTIFY, leading=14)

    story = []

    # ── Header ──────────────────────────────────────────────────────────
    hdr = Table([[
        _p("BioReport AI", ps("ht", fontSize=18, fontName="Helvetica-Bold",
                               textColor=colors.white, spaceAfter=0)),
        _p(f"Genere le {datetime.now().strftime('%d/%m/%Y a %H:%M')}",
           ps("hd", fontSize=8, textColor=_c("#93c5fd"), alignment=TA_LEFT, spaceAfter=0)),
    ]], colWidths=[10*cm, 7*cm])
    hdr.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _c("#1e3a5f")),
        ("TOPPADDING",    (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LEFTPADDING",   (0, 0), (0, -1), 16),
        ("RIGHTPADDING",  (-1, 0), (-1, -1), 16),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",  (1, 0), (1, -1), "RIGHT"),
    ]))
    story.append(hdr)
    story.append(Spacer(1, 0.3*cm))
    story.append(_p("Rapport d'interpretation biologique — Aide a la decision clinique", s_small))
    story.append(_p(f"<b>{label}</b>", ps("lbl", fontSize=10, fontName="Helvetica-Bold",
                                            textColor=_c("#2563eb"), spaceAfter=10)))

    # ── Patient box ─────────────────────────────────────────────────────
    if patient_ctx:
        rows = []
        age = f"{patient_ctx['age']} ans" if patient_ctx.get("age") else None
        sex = patient_ctx.get("sexe") if patient_ctx.get("sexe") not in (None, "—") else None
        if age or sex:
            rows.append([
                _p("AGE", s_label), _p(age or "—", s_val),
                _p("SEXE", s_label), _p(sex or "—", s_val),
            ])
        if patient_ctx.get("motif"):
            rows.append([
                _p("MOTIF", s_label), Paragraph(patient_ctx["motif"], s_val),
                _p("", s_label), _p("", s_val),
            ])
        if patient_ctx.get("antecedents"):
            rows.append([
                _p("ANTECEDENTS", s_label), Paragraph(patient_ctx["antecedents"], s_val),
                _p("", s_label), _p("", s_val),
            ])
        if patient_ctx.get("greffe"):
            gtype = patient_ctx.get("type_greffe", "Transplantation")
            gphase = patient_ctx.get("phase_greffe", "")
            rows.append([
                _p("TRANSPLANT.", s_label), _p(gtype, s_val),
                _p("PHASE", s_label), _p(gphase or "—", s_val),
            ])
            tacro_parts = []
            if patient_ctx.get("tacro_dose") is not None:
                tacro_parts.append(f"Dose : {patient_ctx['tacro_dose']} mg/j")
            if patient_ctx.get("tacro_residuel") is not None:
                tacro_parts.append(f"C0 : {patient_ctx['tacro_residuel']} ng/mL")
            if tacro_parts:
                rows.append([
                    _p("TACROLIMUS", s_label), _p("   |   ".join(tacro_parts), s_val),
                    _p("", s_label), _p("", s_val),
                ])
        if rows:
            pt = Table(rows, colWidths=[3*cm, 5.5*cm, 3*cm, 5.5*cm])
            pt.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), _c("#f8fafc")),
                ("BOX",        (0, 0), (-1, -1), 0.5, _c("#e2e8f0")),
                ("TOPPADDING",    (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING",   (0, 0), (-1, -1), 8),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
            ]))
            story.append(pt)
            story.append(Spacer(1, 0.35*cm))

    # ── Sections ────────────────────────────────────────────────────────
    # Handle intro block (patient context line before first ##)
    intro_split = re.split(r'(?=## \d)', report_text, maxsplit=1)
    if intro_split[0].strip():
        for line in intro_split[0].strip().split('\n'):
            line = line.strip()
            if line and line != '---':
                story.append(_p(line, s_intro))
        story.append(Spacer(1, 0.2*cm))

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
        col_h, col_bg = SECTION_COLOR.get(num, ("#2563eb", "#eff6ff"))

        # Section header
        sec_hdr = Table([[_p(title, ps(f"sh{num}", fontSize=10, fontName="Helvetica-Bold",
                                        textColor=colors.white, spaceAfter=0))]],
                         colWidths=[W])
        sec_hdr.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), _c(col_h)),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ]))
        story.append(sec_hdr)

        # Section body
        body_lines = section[m.end():].strip().split('\n')
        body_paras = []
        for line in body_lines:
            line = line.strip()
            if not line:
                body_paras.append(Spacer(1, 0.15*cm))
                continue
            if line.startswith('- '):
                line = '• ' + line[2:]
            body_paras.append(_p(line, s_body))

        if body_paras:
            body_tbl = Table([[bp] for bp in body_paras], colWidths=[W])
            body_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), _c(col_bg)),
                ("TOPPADDING",    (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING",   (0, 0), (-1, -1), 14),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
            ]))
            story.append(body_tbl)

        story.append(Spacer(1, 0.3*cm))

    # ── Footer ──────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=_c("#e2e8f0")))
    story.append(Spacer(1, 0.2*cm))
    story.append(_p(
        "[!] Outil d'aide a l'interpretation uniquement. Ne remplace pas le jugement du biologiste medical ou du medecin prescripteur.",
        s_disc
    ))
    story.append(_p("BioReport AI · bioreport-ai.streamlit.app", s_disc))

    doc.build(story)
    return buf.getvalue()
