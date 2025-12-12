from xhtml2pdf import pisa
from io import BytesIO
from fastapi.templating import Jinja2Templates
from app.domain.sales.entities import SalesInvoice
from app.domain.auth.entities import User

class PdfService:
    def __init__(self, templates: Jinja2Templates):
        self.templates = templates

    def generate_invoice_pdf(self, invoice: SalesInvoice, partner, company_info: dict = None) -> bytes:
        """
        Generate PDF bytes for a sales invoice.
        company_info can contain: name, address, tax_id, logo_path, etc.
        """
        if company_info is None:
            # Default company info (should be in config/db in future)
            company_info = {
                "name": "La Meva Empresa S.L.",
                "address": "Carrer de la Indústria, 12, Barcelona",
                "tax_id": "B12345678",
                "email": "info@lamevaempresa.com",
                "phone": "+34 93 123 45 67",
                "website": "www.lamevaempresa.com"
            }

        # Calculate totals breakdown if needed (or rely on invoice properties)
        # Prepare context for template
        context = {
            "request": None, # Not needed for pure string rendering usually, but Jinja might complain if using url_for
            "invoice": invoice,
            "partner": partner,
            "company": company_info,
        }

        # Render HTML
        template = self.templates.get_template("sales/invoices/pdf_template.html")
        html_content = template.render(context)

        # Convert to PDF
        buffer = BytesIO()
        pisa_status = pisa.CreatePDF(html_content, dest=buffer)
        
        if pisa_status.err:
            raise Exception("Error generating PDF")

        return buffer.getvalue()
