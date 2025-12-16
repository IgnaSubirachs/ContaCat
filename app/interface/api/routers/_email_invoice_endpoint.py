"""
Email send endpoint for Sales Invoices - append to sales_invoices.py
"""

@router.post("/{invoice_id}/send-email")
async def send_invoice_email(
    invoice_id: str,
    recipient_email: str = Form(None),
    service: SalesInvoiceService = Depends(get_invoice_service)
):
    """Send invoice via email with PDF attachment."""
    invoice = service.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no trobada")
    
    # Get partner
    partner_repo = SqlAlchemyPartnerRepository(SessionLocal)
    partner = partner_repo.find_by_id(invoice.partner_id)
    
    # Get settings
    from app.infrastructure.persistence.settings.repository import SqlAlchemyCompanySettingsRepository
    from app.domain.settings.services import SettingsService
    settings_repo = SqlAlchemyCompanySettingsRepository(SessionLocal)
    settings_service = SettingsService(settings_repo)
    settings = settings_service.get_settings_or_default()
    
    # Generate PDF
    from app.domain.sales.pdf_service import PdfService
    pdf_service = PdfService(templates)
    pdf_bytes = pdf_service.generate_invoice_pdf(invoice, partner, company_settings=settings)
    
    # Send Email
    from app.domain.email.services import EmailService
    email_service = EmailService(settings_service)
    
    # Use provided email or partner's email
    target_email = recipient_email if recipient_email else (partner.email if partner else None)
    
    if not target_email:
        raise HTTPException(status_code=400, detail="No hi ha email del client configurat")
    
    # Attach partner to invoice for email template
    invoice.partner = partner
    
    success = email_service.send_invoice_email(invoice, pdf_bytes, recipient=target_email)
    
    if success:
        return RedirectResponse(url=f"/sales/invoices/{invoice_id}?email_sent=true", status_code=303)
    else:
        raise HTTPException(status_code=500, detail="Error enviant l'email. Verifica la configuració SMTP.")
