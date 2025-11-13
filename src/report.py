# src/report.py
import io
import datetime
from typing import Any, Dict, Tuple

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch

from PIL import Image as PILImage

def build_report(image_bytes: bytes, text: str, results: Dict[str, Any]) -> Tuple[bytes, str]:
    """Generate a PDF report with the analysis results."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Title
    story.append(Paragraph("GreenCheck - Ad Greenwashing Review", styles["h1"]))
    story.append(Spacer(1, 0.2 * inch))

    # Add the analyzed image
    pil_image = PILImage.open(io.BytesIO(image_bytes))
    img = Image(io.BytesIO(image_bytes), width=4*inch, height=4*inch)
    story.append(img)
    story.append(Spacer(1, 0.2 * inch))

    # Add extracted text
    story.append(Paragraph("Extracted Text:", styles["h2"]))
    story.append(Paragraph(text, styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    # Add analysis results
    story.append(Paragraph("Analysis Results:", styles["h2"]))
    story.append(Paragraph(f"Score: {results.get('score', 'N/A')}", styles["Normal"]))
    story.append(Paragraph(f"Level: {results.get('level', 'N/A')}", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    # Add triggers/reasons
    story.append(Paragraph("Key Triggers Identified:", styles["h2"]))
    for reason in results.get("reasons", []):
        story.append(Paragraph(f"- {reason}", styles["Normal"]))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    filename = generate_filename()
    return pdf_bytes, filename

def generate_filename() -> str:
    """Generate a filename for the PDF report."""
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    return f"GreenCheck_Report_{date}.pdf"
