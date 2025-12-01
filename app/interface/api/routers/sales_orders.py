from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request, Form
from typing import List, Optional
from datetime import date
from decimal import Decimal

from app.infrastructure.db.base import SessionLocal
from app.domain.sales.services import SalesOrderService
from app.domain.sales.entities import OrderStatus
from app.infrastructure.persistence.sales.repository import SqlAlchemySalesOrderRepository, SqlAlchemyQuoteRepository
from app.infrastructure.persistence.partners.repository import SqlAlchemyPartnerRepository


router = APIRouter(prefix="/sales/orders", tags=["sales_orders"])
templates = Jinja2Templates(directory="app/interface/web/templates")


def get_order_service():
    """Dependency to get SalesOrderService instance."""
    # Pass SessionLocal factory directly
    order_repo = SqlAlchemySalesOrderRepository(SessionLocal)
    quote_repo = SqlAlchemyQuoteRepository(SessionLocal)
    partner_repo = SqlAlchemyPartnerRepository(SessionLocal)
    return SalesOrderService(order_repo, quote_repo, partner_repo)


@router.get("/", response_class=HTMLResponse)
async def list_orders(request: Request, status: Optional[str] = None):
    """List all sales orders."""
    service = get_order_service()
    
    if status:
        try:
            status_enum = OrderStatus[status.upper()]
            orders = service.list_orders(status=status_enum)
        except KeyError:
            orders = service.list_orders()
    else:
        orders = service.list_orders()
    
    return templates.TemplateResponse("sales/orders/list.html", {
        "request": request,
        "orders": orders,
        "current_status": status
    })


@router.get("/{order_id}", response_class=HTMLResponse)
async def view_order(request: Request, order_id: str):
    """View order details."""
    service = get_order_service()
    order = service.get_order(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Comanda no trobada")
    
    # Get partner details
    partner_repo = SqlAlchemyPartnerRepository(SessionLocal)
    partner = partner_repo.find_by_id(order.partner_id)
    
    return templates.TemplateResponse("sales/orders/view.html", {
        "request": request,
        "order": order,
        "partner": partner
    })


@router.post("/{order_id}/confirm")
async def confirm_order(order_id: str):
    """Confirm a sales order."""
    service = get_order_service()
    
    try:
        order = service.confirm_order(order_id)
        return RedirectResponse(url=f"/sales/orders/{order.id}", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/deliver")
async def deliver_order(order_id: str):
    """Mark order as delivered."""
    service = get_order_service()
    
    try:
        order = service.deliver_order(order_id)
        return RedirectResponse(url=f"/sales/orders/{order.id}", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/cancel")
async def cancel_order(order_id: str):
    """Cancel a sales order."""
    service = get_order_service()
    
    try:
        order = service.cancel_order(order_id)
        return RedirectResponse(url=f"/sales/orders/{order.id}", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/from-quote/{quote_id}")
async def create_from_quote(quote_id: str):
    """Create order from quote."""
    service = get_order_service()
    
    try:
        order = service.create_from_quote(quote_id)
        return RedirectResponse(url=f"/sales/orders/{order.id}", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
