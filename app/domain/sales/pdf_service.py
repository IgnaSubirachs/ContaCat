from fastapi.templating import Jinja2Templates
from app.domain.sales.entities import SalesInvoice
from app.domain.settings.entities import CompanySettings
from app.domain.documents.services import DocumentService

class PdfService:
    def __init__(self, templates: Jinja2Templates):
        self.templates = templates
        self.doc_service = DocumentService()

    def generate_invoice_pdf(self, invoice: SalesInvoice, partner, company_settings: CompanySettings = None) -> bytes:
        """
        Generate PDF bytes for a sales invoice.
        """
        # Prepare context for template
        context = {
            "request": None, 
            "invoice": invoice,
            "partner": partner,
            "company": company_settings,
        }

        # Render HTML
        template = self.templates.get_template("sales/invoices/pdf.html")
        html_content = template.render(context)

        # Convert to PDF
        return self.doc_service.generate_pdf(html_content)
