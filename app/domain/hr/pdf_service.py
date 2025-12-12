from xhtml2pdf import pisa
from io import BytesIO
from fastapi.templating import Jinja2Templates
from app.domain.hr.entities import Payroll, Employee

class PayrollPdfService:
    def __init__(self, templates: Jinja2Templates):
        self.templates = templates

    def generate_payslip_pdf(self, payroll: Payroll, employee: Employee, company_info: dict = None) -> bytes:
        """
        Generate PDF bytes for a payroll payslip.
        """
        if company_info is None:
            # Default company info
            company_info = {
                "name": "La Meva Empresa S.L.",
                "address": "Carrer de la Indústria, 12, Barcelona",
                "tax_id": "B12345678",
                "ccc": "08/123456789" # Codi Compte Cotització SS
            }

        # Calculate SS Breakdown
        ss_total = payroll.social_security_employee # Decimal
        # 4.70 / 6.35 part
        ss_common = (ss_total * 470 / 635).quantize(ss_total) 
        # 1.65 / 6.35 part (remainder to be safe or calc)
        ss_training = ss_total - ss_common

        # Prepare context for template
        context = {
            "request": None, 
            "payroll": payroll,
            "employee": employee,
            "company": company_info,
            "ss_common": ss_common,
            "ss_training": ss_training
        }

        # Render HTML
        template = self.templates.get_template("hr/payrolls/pdf_template.html")
        html_content = template.render(context)

        # Convert to PDF
        buffer = BytesIO()
        pisa_status = pisa.CreatePDF(html_content, dest=buffer)
        
        if pisa_status.err:
            raise Exception("Error generating PDF")

        return buffer.getvalue()
