# src/report.py
import os
from io import BytesIO
from datetime import datetime
from typing import Dict, Any, List

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
)
from reportlab.pdfgen import canvas as pdfcanvas


# ---------- Helpers ----------
def _img_from_bytes(image_bytes: bytes, max_w=16 * cm):
    """
    Return a Platypus Image built from raw image bytes, scaled to max_w.
    Uses ImageReader to probe size; passes a BytesIO stream to Image.
    """
    bio = BytesIO(image_bytes)
    ir = ImageReader(bio)
    iw, ih = ir.getSize()
    if iw <= 0 or ih <= 0:
        return Image(BytesIO(image_bytes))
    scale = min(max_w / float(iw), 1.0)
    # Rewind for Image construction
    bio2 = BytesIO(image_bytes)
    return Image(bio2, width=iw * scale, height=ih * scale)


def _maybe_logo(max_w=3.5 * cm):
    """
    Try to load a logo from assets/logo.png. Return an Image or None.
    No exceptions bubble up to the caller.
    """
    try:
        path = os.path.join("assets", "logo.png")
        if os.path.isfile(path):
            with open(path, "rb") as f:
                return _img_from_bytes(f.read(), max_w=max_w)
    except Exception:
        pass
    return None


def _kv_table(rows: List[List[str]], col_widths=None) -> Table:
    """
    Simple key/value(/notes) table with a light grid and header background.
    """
    t = Table(rows, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("LEADING", (0, 0), (-1, -1), 12),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def _triggers_table(triggers: Dict[str, List[str]]) -> Table:
    """
    2-column table: Category / Occurrences
    """
    data = [["Category", "Occurrences"]]
    for k in sorted(triggers.keys()):
        vals = triggers.get(k) or []
        vals = sorted({v for v in vals if v})
        if not vals:
            continue
        nice = k.replace("_", " ").title()
        data.append([nice, ", ".join(vals)])

    if len(data) == 1:
        data.append(["—", "No obvious trigger phrases detected."])

    col_widths = [6.5 * cm, 8.5 * cm]
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("LEADING", (0, 0), (-1, -1), 12),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def _filename_from_label(ai_label: str) -> str:
    """
    LeafCheck_Report_YYYY-MM-DD_slug.pdf
    """
    date = datetime.now().strftime("%Y-%m-%d")
    tag = (ai_label or "analysis").strip().lower().replace(" ", "-")
    safe = "".join(ch for ch in tag if ch.isalnum() or ch in ("-", "_"))
    return f"LeafCheck_Report_{date}_{safe or 'analysis'}.pdf"


def _risk_color(level: str):
    """
    Background color for the 'Level' cell in Risk Summary.
    """
    lv = (level or "").strip().lower()
    if lv == "high":
        return colors.HexColor("#ffb3b3")   # soft red
    if lv == "medium":
        return colors.HexColor("#fff3b0")   # soft yellow
    if lv == "low":
        return colors.HexColor("#b5e48c")   # soft green
    return colors.whitesmoke


def _footer(c: pdfcanvas.Canvas, doc):
    """
    Footer with page number + small label.
    """
    page = c.getPageNumber()
    text = f"LeafCheck — confidential analysis  |  Page {page}"
    c.setFont("Helvetica", 8)
    # subtle top border line for the footer area
    c.setStrokeColor(colors.lightgrey)
    c.line(1.6 * cm, 1.4 * cm, A4[0] - 1.6 * cm, 1.4 * cm)
    c.setFillColor(colors.black)
    c.drawCentredString(A4[0] / 2, 1.1 * cm, text)


# ---------- Main ----------
def build_report(image_bytes: bytes, extracted_text: str, results: Dict[str, Any]):
    """
    Build the PDF report and return (pdf_bytes: bytes, filename: str).
    """
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=1.6 * cm,
        leftMargin=1.6 * cm,
        topMargin=1.4 * cm,
        bottomMargin=1.8 * cm,  # tiny extra space for footer
        title="LeafCheck — Ad Greenwashing Review",
        author="LeafCheck",
        subject="Greenwashing risk analysis",
        creator="LeafCheck",
    )

    styles = getSampleStyleSheet()
    H1 = styles["Title"]
    H1.fontName = "Helvetica-Bold"
    H1.fontSize = 20
    H1.leading = 24

    H2 = styles["Heading2"]
    H2.fontName = "Helvetica-Bold"
    H2.fontSize = 14
    H2.leading = 18
    H2.spaceBefore = 8
    H2.spaceAfter = 4

    body = styles["BodyText"]
    body.fontName = "Helvetica"
    body.fontSize = 10.5
    body.leading = 14

    small = ParagraphStyle(
        "small",
        parent=body,
        fontSize=9.2,
        leading=12,
        textColor=colors.HexColor("#444444"),
    )

    center_small = ParagraphStyle(
        "center_small",
        parent=small,
        alignment=TA_CENTER
    )

    story = []

    # --- Header: logo (optional) + title/date
    logo = _maybe_logo()
    if logo:
        # put logo then a tiny spacer before title
        story.append(logo)
        story.append(Spacer(1, 0.2 * cm))

    story.append(Paragraph("LeafCheck — Ad Greenwashing Review", H1))
    story.append(Paragraph(datetime.now().strftime("%d %b %Y, %H:%M"), center_small))
    story.append(Spacer(1, 0.4 * cm))

    # --- Ad image
    story.append(Paragraph("Ad Screenshot", H2))
    try:
        story.append(_img_from_bytes(image_bytes, max_w=16 * cm))
    except Exception:
        story.append(Paragraph("Image preview unavailable.", small))
    story.append(Spacer(1, 0.3 * cm))

    # --- Risk summary
    score = int(results.get("score", 0) or 0)
    level = str(results.get("level", "Unknown") or "Unknown")
    ai_label = str(results.get("ai_label", "—") or "—")
    try:
        ai_conf = float(results.get("ai_confidence", 0.0) or 0.0)
    except (TypeError, ValueError):
        ai_conf = 0.0

    story.append(Paragraph("Risk Summary", H2))
    risk_rows = [
        ["Metric", "Value", "Notes"],
        ["Risk Score", str(score), ""],
        ["Level", level, ""],
        ["AI Assessment", ai_label, f"{ai_conf:.1f}% confidence"],
    ]
    risk_tbl = _kv_table(risk_rows, col_widths=[4.0 * cm, 4.0 * cm, 7.0 * cm])

    # Colorize the "Level" value cell (row index 2, col index 1)
    bg = _risk_color(level)
    risk_tbl.setStyle(TableStyle([
        ("BACKGROUND", (1, 2), (1, 2), bg),
    ]))

    story.append(risk_tbl)
    story.append(Spacer(1, 0.4 * cm))

    # --- Triggered categories
    triggers = results.get("triggers", {}) or {}
    story.append(Paragraph("Triggered Categories", H2))
    story.append(_triggers_table(triggers))
    story.append(Spacer(1, 0.4 * cm))

    # --- Recommendations
    recs = results.get("recommendations", []) or []
    story.append(Paragraph("Recommendations", H2))
    if recs:
        for tip in recs:
            story.append(Paragraph(f"• {tip}", body))
            story.append(Spacer(1, 0.06 * cm))
    else:
        story.append(Paragraph("No recommendations generated.", small))
    story.append(Spacer(1, 0.4 * cm))

    # --- Extracted text
    story.append(Paragraph("Extracted Text (OCR)", H2))
    # safe HTML escaping + line breaks
    cleaned = (extracted_text or "")
    cleaned = cleaned.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    cleaned = cleaned.replace("\n", "<br/>")
    story.append(Paragraph(cleaned, body))

    # --- Build with footer on every page
    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)

    pdf_bytes = buf.getvalue()
    buf.close()

    # Filename
    fname = _filename_from_label(ai_label)
    return pdf_bytes, fname
