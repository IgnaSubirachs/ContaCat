from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.domain.auth.dependencies import get_current_active_user
from app.infrastructure.java_erp_client import JavaErpClient, JavaErpClientError
from app.interface.api.templates import templates

router = APIRouter(
    prefix="/sales/orders",
    tags=["sales_orders"],
    dependencies=[Depends(get_current_active_user)],
)


def get_java_erp_client() -> JavaErpClient:
    return JavaErpClient()


@router.get("/", response_class=HTMLResponse)
async def list_orders(
    request: Request,
    status: Optional[str] = None,
    client: JavaErpClient = Depends(get_java_erp_client),
):
    try:
        orders = [_to_order_view(order) for order in client.list_sales_orders(status.upper() if status else None)]
    except JavaErpClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return templates.TemplateResponse("sales/orders/list.html", {
        "request": request,
        "orders": orders,
        "current_status": status,
    })


@router.get("/{order_id}", response_class=HTMLResponse)
async def view_order(
    request: Request,
    order_id: str,
    client: JavaErpClient = Depends(get_java_erp_client),
):
    try:
        order = _to_order_view(client.get_sales_order(order_id))
        partner = _to_partner_view(client.get_partner(order.partner_id))
    except JavaErpClientError as exc:
        status_code = 404 if "No s'ha trobat" in str(exc) else 502
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc

    return templates.TemplateResponse("sales/orders/view.html", {
        "request": request,
        "order": order,
        "partner": partner,
    })


@router.post("/{order_id}/confirm")
async def confirm_order(
    order_id: str,
    client: JavaErpClient = Depends(get_java_erp_client),
):
    try:
        client.confirm_sales_order(order_id)
        return RedirectResponse(url=f"/sales/orders/{order_id}", status_code=303)
    except JavaErpClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{order_id}/deliver")
async def deliver_order(
    order_id: str,
    client: JavaErpClient = Depends(get_java_erp_client),
):
    try:
        client.deliver_sales_order(order_id)
        return RedirectResponse(url=f"/sales/orders/{order_id}", status_code=303)
    except JavaErpClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: str,
    client: JavaErpClient = Depends(get_java_erp_client),
):
    try:
        client.cancel_sales_order(order_id)
        return RedirectResponse(url=f"/sales/orders/{order_id}", status_code=303)
    except JavaErpClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/from-quote/{quote_id}")
async def create_from_quote(
    quote_id: str,
    client: JavaErpClient = Depends(get_java_erp_client),
):
    try:
        created = client.create_sales_order_from_quote(quote_id, date.today())
        return RedirectResponse(url=f"/sales/orders/{created['id']}", status_code=303)
    except JavaErpClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _to_order_view(payload: dict) -> SimpleNamespace:
    lines = [
        SimpleNamespace(
            product_code=line["productCode"],
            description=line["description"],
            quantity=Decimal(str(line["quantity"])),
            unit_price=Decimal(str(line["unitPrice"])),
            total=Decimal(str(line["total"])),
        )
        for line in payload.get("lines", [])
    ]
    return SimpleNamespace(
        id=payload["id"],
        order_number=payload["orderNumber"],
        order_date=date.fromisoformat(payload["orderDate"]),
        partner_id=payload["partnerId"],
        partner_name=payload.get("partnerName", payload["partnerId"]),
        status=SimpleNamespace(value=payload["status"]),
        delivery_date=date.fromisoformat(payload["deliveryDate"]) if payload.get("deliveryDate") else None,
        delivery_address=payload.get("deliveryAddress") or "",
        subtotal=Decimal(str(payload["subtotal"])),
        total_tax=Decimal(str(payload["totalTax"])),
        total=Decimal(str(payload["total"])),
        lines=lines,
        quote_id=payload.get("quoteId"),
        quote_number=payload.get("quoteNumber"),
        notes=payload.get("notes") or "",
    )


def _to_partner_view(payload: dict) -> SimpleNamespace:
    return SimpleNamespace(
        id=payload["id"],
        name=payload["name"],
        tax_id=payload["taxId"],
    )
