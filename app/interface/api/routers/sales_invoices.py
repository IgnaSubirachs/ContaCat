from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request, Form
from typing import List, Optional
from datetime import date
from decimal import Decimal

from app.infrastructure.db.base import SessionLocal
from app.domain.sales.services import SalesInvoiceService
from app.domain.sales.entities import InvoiceStatus
from app.domain.accounting.services import AccountingService
from app.infrastructure.persistence.sales.repository import (
    SqlAlchemySalesInvoiceRepository, SqlAlchemySalesOrderRepository
)
from app.infrastructure.persistence.partners.repository import SqlAlchemyPartnerRepository
from app.infrastructure.persistence.accounts.repository import SqlAlchemyAccountRepository
from app.infrastructure.persistence.accounting.repository import SqlAlchemyJournalRepository


router = APIRouter(prefix="/sales/invoices", tags=["sales_invoices"])
from app.interface.api.templates import templates


def get_invoice_service():
    """Dependency to get SalesInvoiceService instance."""
    # Pass SessionLocal factory directly
    invoice_repo = SqlAlchemySalesInvoiceRepository(SessionLocal)
    order_repo = SqlAlchemySalesOrderRepository(SessionLocal)
    partner_repo = SqlAlchemyPartnerRepository(SessionLocal)
    account_repo = SqlAlchemyAccountRepository(SessionLocal)
    journal_repo = SqlAlchemyJournalRepository(SessionLocal)
    accounting_service = AccountingService(account_repo, journal_repo)
    
    from app.domain.accounting.mapping_service import AccountMappingService
    mapping_service = AccountMappingService()
    
    from app.infrastructure.persistence.audit.repository import SqlAlchemyAuditRepository
    from app.domain.audit.services import AuditService
    audit_repo = SqlAlchemyAuditRepository(SessionLocal)
    audit_service = AuditService(audit_repo)

    # Inventory Service Injection
    from app.domain.inventory.services import InventoryService
    from app.infrastructure.persistence.inventory.repositories import SqlAlchemyStockItemRepository, SqlAlchemyStockMovementRepository
    stock_item_repo = SqlAlchemyStockItemRepository(SessionLocal)
    stock_movement_repo = SqlAlchemyStockMovementRepository(SessionLocal)
    inventory_service = InventoryService(stock_item_repo, stock_movement_repo)
    
    return SalesInvoiceService(invoice_repo, order_repo, partner_repo, accounting_service, mapping_service, audit_service, inventory_service)


@router.get("/", response_class=HTMLResponse)
async def list_invoices(request: Request, status: Optional[str] = None):
    """List all sales invoices."""
    service = get_invoice_service()
    
    if status:
        try:
            status_enum = InvoiceStatus[status.upper()]
            invoices = service.list_invoices(status=status_enum)
        except KeyError:
            invoices = service.list_invoices()
    else:
        invoices = service.list_invoices()
    
    return templates.TemplateResponse("sales/invoices/list.html", {
        "request": request,
        "invoices": invoices,
        "current_status": status
    })


@router.get("/{invoice_id}", response_class=HTMLResponse)
async def view_invoice(request: Request, invoice_id: str):
    """View invoice details."""
    service = get_invoice_service()
    invoice = service.get_invoice(invoice_id)
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no trobada")
    
    # Get partner details
    partner_repo = SqlAlchemyPartnerRepository(SessionLocal)
    partner = partner_repo.find_by_id(invoice.partner_id)
    
    return templates.TemplateResponse("sales/invoices/view.html", {
        "request": request,
        "invoice": invoice,
        "partner": partner
    })


@router.post("/{invoice_id}/post")
async def post_invoice(invoice_id: str):
    """Post invoice and create journal entry."""
    service = get_invoice_service()
    
    try:
        invoice = service.post_invoice(invoice_id)
        return RedirectResponse(url=f"/sales/invoices/{invoice.id}", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{invoice_id}/mark-paid")
async def mark_as_paid(invoice_id: str):
    """Mark invoice as paid."""
    service = get_invoice_service()
    
    try:
        invoice = service.mark_as_paid(invoice_id)
        return RedirectResponse(url=f"/sales/invoices/{invoice.id}", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/from-order/{order_id}")
async def create_from_order(order_id: str, series: str = Form("A")):
    """Create invoice from order."""
    service = get_invoice_service()
    
    try:
        invoice = service.create_from_order(order_id, series=series)
        return RedirectResponse(url=f"/sales/invoices/{invoice.id}", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

from fastapi import Response
from app.domain.sales.pdf_service import PdfService

@router.get("/{invoice_id}/pdf")
async def get_invoice_pdf(invoice_id: str):
    """Generate and download PDF for invoice."""
    service = get_invoice_service()
    invoice = service.get_invoice(invoice_id)
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no trobada")
        
    partner_repo = SqlAlchemyPartnerRepository(SessionLocal)
    partner = partner_repo.find_by_id(invoice.partner_id)
    
    # Get Company Settings
    from app.infrastructure.persistence.settings.repository import SqlAlchemyCompanySettingsRepository
    from app.domain.settings.services import SettingsService
    settings_repo = SqlAlchemyCompanySettingsRepository(SessionLocal)
    settings_service = SettingsService(settings_repo)
    settings = settings_service.get_settings_or_default()
    
    pdf_service = PdfService(templates)
    pdf_bytes = pdf_service.generate_invoice_pdf(invoice, partner, company_settings=settings)
    
    filename = f"Factura_{invoice.invoice_number}.pdf"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
