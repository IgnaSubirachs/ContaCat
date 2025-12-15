import io
from typing import Optional
from xhtml2pdf import pisa
import logging

logger = logging.getLogger(__name__)

class DocumentService:
    def generate_pdf(self, html_content: str) -> bytes:
        """
        Generates a PDF from HTML content using xhtml2pdf.
        Returns the PDF bytes.
        """
        buffer = io.BytesIO()
        
        # Configure pisa to handle errors gracefully?
        # xhtml2pdf expects html string (unicode) or bytes.
        
        try:
            pisa_status = pisa.CreatePDF(
                html_content,
                dest=buffer,
                encoding='utf-8'
            )
        except Exception as e:
            logger.error(f"xhtml2pdf crashed: {e}")
            raise e
            
        if pisa_status.err:
            error_msg = f"PDF generation error: {pisa_status.err}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        return buffer.getvalue()
