import io
import datetime
from typing import Dict, Any, Tuple
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as ReportLabImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from PIL import Image as PILImage

class PDFService:
    def __init__(self, image_bytes: bytes, analysis_data: Dict[str, Any]):
        self.image_bytes = image_bytes
        self.analysis_data = analysis_data
        self.styles = getSampleStyleSheet()

    def generate_report(self) -> Tuple[bytes, str]:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = self._build_story()
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        filename = self._generate_filename()
        return pdf_bytes, filename

    def _build_story(self):
        story = []
        story.append(Paragraph("GreenCheck - Analysis Report", self.styles["h1"]))
        story.append(Spacer(1, 0.2 * inch))

        # Add image
        pil_image = PILImage.open(io.BytesIO(self.image_bytes))
        img = ReportLabImage(io.BytesIO(self.image_bytes), width=4*inch, height=4*inch)
        story.append(img)
        story.append(Spacer(1, 0.2 * inch))

        # Add extracted text
        story.append(Paragraph("Extracted Text", self.styles["h2"]))
        story.append(Paragraph(self.analysis_data.get("text", ""), self.styles["Normal"]))
        story.append(Spacer(1, 0.2 * inch))

        # Add analysis results
        story.append(Paragraph("Analysis Results", self.styles["h2"]))
        story.append(Paragraph(f"Risk Score: {self.analysis_data.get('score', 'N/A')}", self.styles["Normal"]))
        story.append(Paragraph(f"Risk Level: {self.analysis_data.get('level', 'N/A')}", self.styles["Normal"]))
        story.append(Spacer(1, 0.2 * inch))

        # Add reasons
        story.append(Paragraph("Reasons", self.styles["h2"]))
        for reason in self.analysis_data.get("reasons", []):
            story.append(Paragraph(f"- {reason}", self.styles["Normal"]))

        return story

    def _generate_filename(self) -> str:
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        return f"GreenCheck_Report_{date}.pdf"
