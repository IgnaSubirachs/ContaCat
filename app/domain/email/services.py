"""
Email Service - Send invoices, payslips, and reports via email.
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path
from typing import List, Optional
import logging

from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails with attachments."""
    
    def __init__(self, settings_service):
        """
        Initialize EmailService with settings.
        
        Args:
            settings_service: SettingsService instance to fetch SMTP config
        """
        self._settings_service = settings_service
        self._templates_dir = Path(__file__).parent.parent.parent.parent / "frontend" / "email_templates"
        self._jinja_env = Environment(loader=FileSystemLoader(str(self._templates_dir)))
    
    def send_email(
        self,
        to: str,
        subject: str,
        html_body: str,
        attachments: Optional[List[tuple]] = None,
        cc: Optional[str] = None
    ) -> bool:
        """
        Send an email with optional attachments.
        
        Args:
            to: Recipient email address
            subject: Email subject
            html_body: HTML content of the email
            attachments: List of (filename, file_bytes) tuples
            cc: Optional CC email address
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            settings = self._settings_service.get_settings()
            
            # Validate SMTP configuration
            if not settings.smtp_host or not settings.smtp_user:
                logger.error("SMTP not configured in settings")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{settings.smtp_from_name} <{settings.smtp_from_email or settings.smtp_user}>"
            msg['To'] = to
            if cc:
                msg['Cc'] = cc
            
            # Attach HTML body
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            # Attach files
            if attachments:
                for filename, file_bytes in attachments:
                    part = MIMEApplication(file_bytes, Name=filename)
                    part['Content-Disposition'] = f'attachment; filename="{filename}"'
                    msg.attach(part)
            
            # Send email
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                if settings.smtp_use_tls:
                    server.starttls()
                
                if settings.smtp_password:
                    server.login(settings.smtp_user, settings.smtp_password)
                
                recipients = [to]
                if cc:
                    recipients.append(cc)
                    
                server.sendmail(
                    settings.smtp_from_email or settings.smtp_user,
                    recipients,
                    msg.as_string()
                )
            
            logger.info(f"Email sent successfully to {to}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_invoice_email(self, invoice, pdf_bytes: bytes, recipient: Optional[str] = None) -> bool:
        """
        Send invoice via email with PDF attachment.
        
        Args:
            invoice: SalesInvoice entity
            pdf_bytes: Generated PDF bytes
            recipient: Override recipient (defaults to partner email)
            
        Returns:
            True if sent successfully
        """
        recipient_email = recipient or invoice.partner.email
        if not recipient_email:
            logger.error(f"No email for partner {invoice.partner.name}")
            return False
        
        settings = self._settings_service.get_settings()
        
        # Render email template
        template = self._jinja_env.get_template('invoice_email.html')
        html_body = template.render(
            invoice=invoice,
            company_name=settings.company_name,
            company_logo=settings.logo_path
        )
        
        subject = f"Factura {invoice.invoice_number} - {settings.company_name}"
        filename = f"Factura_{invoice.invoice_number}.pdf"
        
        return self.send_email(
            to=recipient_email,
            subject=subject,
            html_body=html_body,
            attachments=[(filename, pdf_bytes)]
        )
    
    def send_payslip_email(self, payroll, employee, pdf_bytes: bytes) -> bool:
        """
        Send payslip to employee via email.
        
        Args:
            payroll: Payroll entity
            employee: Employee entity
            pdf_bytes: Generated payslip PDF
            
        Returns:
            True if sent successfully
        """
        if not employee.email:
            logger.error(f"No email for employee {employee.name}")
            return False
        
        settings = self._settings_service.get_settings()
        
        # Render email template
        template = self._jinja_env.get_template('payslip_email.html')
        html_body = template.render(
            payroll=payroll,
            employee=employee,
            company_name=settings.company_name
        )
        
        subject = f"Nòmina {payroll.period_month}/{payroll.period_year} - {settings.company_name}"
        filename = f"Nomina_{payroll.period_month}_{payroll.period_year}_{employee.name.replace(' ', '_')}.pdf"
        
        return self.send_email(
            to=employee.email,
            subject=subject,
            html_body=html_body,
            attachments=[(filename, pdf_bytes)]
        )
    
    def send_report_email(
        self,
        report_name: str,
        recipient: str,
        pdf_bytes: bytes,
        message: Optional[str] = None
    ) -> bool:
        """
        Send financial report via email.
        
        Args:
            report_name: Name of the report (e.g., "Balance Sheet")
            recipient: Recipient email
            pdf_bytes: Generated report PDF
            message: Optional custom message
            
        Returns:
            True if sent successfully
        """
        settings = self._settings_service.get_settings()
        
        # Render email template
        template = self._jinja_env.get_template('report_email.html')
        html_body = template.render(
            report_name=report_name,
            company_name=settings.company_name,
            custom_message=message
        )
        
        subject = f"{report_name} - {settings.company_name}"
        filename = f"{report_name.replace(' ', '_')}.pdf"
        
        return self.send_email(
            to=recipient,
            subject=subject,
            html_body=html_body,
            attachments=[(filename, pdf_bytes)]
        )
