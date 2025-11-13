from pydantic import BaseModel

class ReportResponse(BaseModel):
    # This schema is a placeholder for now.
    # In a real application, you might want to define the structure of the PDF report data.
    detail: str = "PDF report generated successfully."
