"""
SII Submit Endpoint for Sales Invoices
Add this to app/interface/api/routers/sales_invoices.py
"""

@router.post("/{invoice_id}/submit-sii")
async def submit_invoice_to_sii(
    invoice_id: str,
    service: SalesInvoiceService = Depends(get_invoice_service)
):
    """Submit posted invoice to AEAT SII."""
    invoice = service.get_invoice(invoice_id)
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no trobada") 
    
    if invoice.status != InvoiceStatus.POSTED:
        raise HTTPException(status_code=400, detail="Només factures comptabilitzades")
    
    # Get settings and SII service
    from app.infrastructure.persistence.settings.repository import SqlAlchemyCompanySettingsRepository
    from app.domain.settings.services import SettingsService
    from app.infrastructure.db.base import SessionLocal
   
    settings_repo = SqlAlchemyCompanySettingsRepository(SessionLocal)
    settings_service = SettingsService(settings_repo)
    
    from app.domain.sii.services import SIIService
    sii_service = SIIService(settings_service)
    
    # Submit to SII
    submission = sii_service.submit_sales_invoice(invoice)
    
    # Redirect back with status
    if submission.status.value in ["ACCEPTED", "SENT"]:
        return RedirectResponse(
            url=f"/sales/invoices/{invoice_id}?sii_success=true&csv={submission.csv}",
            status_code=303
        )
    else:
        return RedirectResponse(
            url=f"/sales/invoices/{invoice_id}?sii_error={submission.error_message}",
            status_code=303
        )
