"""Purchase router with API endpoints."""
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

from app.interface.api.templates import templates
from app.infrastructure.db.base import SessionLocal

from app.domain.purchases.entities import PurchaseOrderLine, PurchaseInvoiceLine
from app.domain.purchases.services import PurchaseOrderService, PurchaseInvoiceService

router = APIRouter(prefix="/purchases", tags=["purchases"])


def get_purchase_services():
    """Get purchase services."""
    from app.infrastructure.persistence.purchases.repository import (
        SqlAlchemyPurchaseOrderRepository,
        SqlAlchemyPurchaseInvoiceRepository
    )
    from app.infrastructure.persistence.partners.repository import SqlAlchemyPartnerRepository
    from app.infrastructure.persistence.accounts.repository import SqlAlchemyAccountRepository
    from app.infrastructure.persistence.accounting.repository import SqlAlchemyJournalRepository
    from app.domain.accounting.services import AccountingService
    from app.domain.accounting.mapping_service import AccountMappingService
    
    order_repo = SqlAlchemyPurchaseOrderRepository(SessionLocal)
    invoice_repo = SqlAlchemyPurchaseInvoiceRepository(SessionLocal)
    partner_repo = SqlAlchemyPartnerRepository(SessionLocal)
    account_repo = SqlAlchemyAccountRepository(SessionLocal)
    journal_repo = SqlAlchemyJournalRepository(SessionLocal)
    
    accounting_service = AccountingService(account_repo, journal_repo)
    mapping_service = AccountMappingService()
    
    order_service = PurchaseOrderService(order_repo, partner_repo)
    invoice_service = PurchaseInvoiceService(
        invoice_repo,
        order_repo,
        partner_repo,
        accounting_service,
        mapping_service
    )
    
    return order_service, invoice_service


# PURCHASE ORDERS
@router.get("/orders", response_class=HTMLResponse)
async def list_orders(request: Request):
    """List purchase orders."""
    order_service, _ = get_purchase_services()
    orders = order_service.list_orders()
    
    # Get partners for display
    partner_repo = SqlAlchemyPartnerRepository(SessionLocal)
    partners = {p.id: p for p in partner_repo.list_all()}
    
    return templates.TemplateResponse("purchases/orders/list.html", {
        "request": request,
        "orders": orders,
        "partners": partners
    })


@router.get("/orders/new", response_class=HTMLResponse)
async def new_order_form(request: Request):
    """Create order form."""
    partner_repo = SqlAlchemyPartnerRepository(SessionLocal)
    partners = partner_repo.list_all()
    
    return templates.TemplateResponse("purchases/orders/create.html", {
        "request": request,
        "partners": partners
    })


@router.post("/orders")
async def create_order(
    partner_id: str = Form(...),
    description_1: str = Form(...),
    quantity_1: str = Form(...),
    unit_price_1: str = Form(...),
    notes: str = Form("")
):
    """Create purchase order."""
    order_service, _ = get_purchase_services()
    
    # Build lines (simplified for MVP)
    lines = [
        PurchaseOrderLine(
            description=description_1,
            quantity=Decimal(quantity_1),
            unit_price=Decimal(unit_price_1)
        )
    ]
    
    order = order_service.create_order(
        partner_id=partner_id,
        lines=lines,
        notes=notes
    )
    
    return RedirectResponse(url=f"/purchases/orders/{order.id}", status_code=303)


@router.get("/orders/{order_id}", response_class=HTMLResponse)
async def view_order(request: Request, order_id: str):
    """View order details."""
    order_service, _ = get_purchase_services()
    order = order_service.get_order(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    partner_repo = SqlAlchemyPartnerRepository(SessionLocal)
    partner = partner_repo.find_by_id(order.partner_id)
    
    return templates.TemplateResponse("purchases/orders/view.html", {
        "request": request,
        "order": order,
        "partner": partner
    })


@router.post("/orders/{order_id}/confirm")
async def confirm_order(order_id: str):
    """Confirm purchase order."""
    order_service, _ = get_purchase_services()
    order_service.confirm_order(order_id)
    return RedirectResponse(url=f"/purchases/orders/{order_id}", status_code=303)


@router.post("/orders/{order_id}/receive")
async def receive_order(order_id: str):
    """Receive purchase order."""
    order_service, _ = get_purchase_services()
    order_service.receive_order(order_id)
    return RedirectResponse(url=f"/purchases/orders/{order_id}", status_code=303)


# PURCHASE INVOICES
@router.get("/invoices", response_class=HTMLResponse)
async def list_invoices(request: Request):
    """List purchase invoices."""
    _, invoice_service = get_purchase_services()
    invoices = invoice_service.list_invoices()
    
    partner_repo = SqlAlchemyPartnerRepository(SessionLocal)
    partners = {p.id: p for p in partner_repo.list_all()}
    
    return templates.TemplateResponse("purchases/invoices/list.html", {
        "request": request,
        "invoices": invoices,
        "partners": partners
    })


@router.get("/invoices/new", response_class=HTMLResponse)
async def new_invoice_form(request: Request):
    """Create invoice form."""
    partner_repo = SqlAlchemyPartnerRepository(SessionLocal)
    partners = partner_repo.list_all()
    
    return templates.TemplateResponse("purchases/invoices/create.html", {
        "request": request,
        "partners": partners
    })


@router.post("/invoices")
async def create_invoice(
    partner_id: str = Form(...),
    supplier_reference: str = Form(""),
    description_1: str = Form(...),
    quantity_1: str = Form(...),
    unit_price_1: str = Form(...),
    notes: str = Form("")
):
    """Create purchase invoice."""
    _, invoice_service = get_purchase_services()
    
    lines = [
        PurchaseInvoiceLine(
            description=description_1,
            quantity=Decimal(quantity_1),
            unit_price=Decimal(unit_price_1)
        )
    ]
    
    invoice = invoice_service.create_invoice(
        partner_id=partner_id,
        supplier_reference=supplier_reference,
        lines=lines,
        notes=notes
    )
    
    return RedirectResponse(url=f"/purchases/invoices/{invoice.id}", status_code=303)


@router.get("/invoices/{invoice_id}", response_class=HTMLResponse)
async def view_invoice(request: Request, invoice_id: str):
    """View invoice details."""
    _, invoice_service = get_purchase_services()
    invoice = invoice_service.get_invoice(invoice_id)
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    partner_repo = SqlAlchemyPartnerRepository(SessionLocal)
    partner = partner_repo.find_by_id(invoice.partner_id)
    
    return templates.TemplateResponse("purchases/invoices/view.html", {
        "request": request,
        "invoice": invoice,
        "partner": partner
    })


@router.post("/invoices/{invoice_id}/post")
async def post_invoice(invoice_id: str):
    """Post invoice to accounting."""
    _, invoice_service = get_purchase_services()
    invoice_service.post_invoice(invoice_id)
    return RedirectResponse(url=f"/purchases/invoices/{invoice_id}", status_code=303)


@router.post("/invoices/{invoice_id}/mark-paid")
async def mark_invoice_paid(
    invoice_id: str,
    amount: str = Form(...),
    payment_date: str = Form(None)
):
    """Mark invoice as paid."""
    _, invoice_service = get_purchase_services()
    
    pay_date = datetime.strptime(payment_date, "%Y-%m-%d").date() if payment_date else date.today()
    
    invoice_service.mark_paid(
        invoice_id=invoice_id,
        payment_date=pay_date,
        amount=Decimal(amount)
    )
    return RedirectResponse(url=f"/purchases/invoices/{invoice_id}", status_code=303)
