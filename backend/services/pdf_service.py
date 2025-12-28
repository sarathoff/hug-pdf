from weasyprint import HTML, CSS
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

class PDFService:
    @staticmethod
    def generate_pdf(html_content: str) -> bytes:
        """Convert HTML to PDF and return as bytes"""
        try:
            # Create a BytesIO buffer
            pdf_buffer = BytesIO()
            
            # Generate PDF from HTML
            HTML(string=html_content).write_pdf(pdf_buffer)
            
            # Get the PDF bytes
            pdf_bytes = pdf_buffer.getvalue()
            pdf_buffer.close()
            
            logger.info("Successfully generated PDF")
            return pdf_bytes
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise