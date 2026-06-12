from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.domain.auth.dependencies import get_current_active_user
from app.infrastructure.java_erp_client import JavaErpClient, JavaErpClientError
from app.interface.api.templates import templates

router = APIRouter(
    prefix="/quotes",
    tags=["quotes"],
    dependencies=[Depends(get_current_active_user)],
)


def get_java_erp_client() -> JavaErpClient:
    return JavaErpClient()


@router.get("/", response_class=HTMLResponse)
async def list_quotes(
    request: Request,
    status: Optional[str] = None,
    client: JavaErpClient = Depends(get_java_erp_client),
):
    try:
        quotes = [_to_quote_view(quote) for quote in client.list_quotes(status=status.upper() if status else None)]
    except JavaErpClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return templates.TemplateResponse("quotes/list.html", {
        "request": request,
        "quotes": quotes,
        "current_status": status,
    })


@router.get("/create", response_class=HTMLResponse)
async def create_quote_form(
    request: Request,
    client: JavaErpClient = Depends(get_java_erp_client),
):
    try:
        customers = [_to_partner_view(partner) for partner in client.list_partners("CUSTOMER")]
    except JavaErpClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return templates.TemplateResponse("quotes/create.html", {
        "request": request,
        "customers": customers,
        "today": date.today().isoformat(),
    })


@router.post("/create")
async def create_quote(
    partner_id: str = Form(...),
    quote_date: str = Form(...),
    valid_days: int = Form(30),
    notes: str = Form(""),
    product_code: str = Form(...),
    description: str = Form(...),
    quantity: Decimal = Form(...),
    unit_price: Decimal = Form(...),
    discount_percent: Decimal = Form(0),
    tax_rate: Decimal = Form(21),
    client: JavaErpClient = Depends(get_java_erp_client),
):
    try:
        quote_date_obj = date.fromisoformat(quote_date)
        created = client.create_quote(
            partner_id=partner_id,
            quote_date=quote_date_obj,
            valid_until=quote_date_obj + timedelta(days=valid_days),
            lines=[{
                "productCode": product_code,
                "description": description,
                "quantity": str(quantity),
                "unitPrice": str(unit_price),
                "discountPercent": str(discount_percent),
                "taxRate": str(tax_rate),
            }],
            notes=notes,
        )
        return RedirectResponse(url=f"/quotes/{created['id']}", status_code=303)
    except JavaErpClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{quote_id}", response_class=HTMLResponse)
async def view_quote(
    request: Request,
    quote_id: str,
    client: JavaErpClient = Depends(get_java_erp_client),
):
    try:
        quote = _to_quote_view(client.get_quote(quote_id))
        partner = _to_partner_view(client.get_partner(quote.partner_id))
    except JavaErpClientError as exc:
        status_code = 404 if "No s'ha trobat" in str(exc) else 502
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc

    return templates.TemplateResponse("quotes/view.html", {
        "request": request,
        "quote": quote,
        "partner": partner,
    })


@router.post("/{quote_id}/send")
async def send_quote(
    quote_id: str,
    client: JavaErpClient = Depends(get_java_erp_client),
):
    try:
        client.send_quote(quote_id)
        return RedirectResponse(url=f"/quotes/{quote_id}", status_code=303)
    except JavaErpClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{quote_id}/accept")
async def accept_quote(
    quote_id: str,
    client: JavaErpClient = Depends(get_java_erp_client),
):
    try:
        client.accept_quote(quote_id)
        return RedirectResponse(url=f"/quotes/{quote_id}", status_code=303)
    except JavaErpClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{quote_id}/reject")
async def reject_quote(
    quote_id: str,
    client: JavaErpClient = Depends(get_java_erp_client),
):
    try:
        client.reject_quote(quote_id)
        return RedirectResponse(url=f"/quotes/{quote_id}", status_code=303)
    except JavaErpClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{quote_id}/delete")
async def delete_quote(
    quote_id: str,
    client: JavaErpClient = Depends(get_java_erp_client),
):
    try:
        client.delete_quote(quote_id)
        return RedirectResponse(url="/quotes/", status_code=303)
    except JavaErpClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/list")
async def api_list_quotes(
    status: Optional[str] = None,
    client: JavaErpClient = Depends(get_java_erp_client),
):
    quotes = client.list_quotes(status=status.upper() if status else None)
    return {
        "quotes": [
            {
                "id": quote["id"],
                "quote_number": quote["quoteNumber"],
                "quote_date": quote["quoteDate"],
                "valid_until": quote["validUntil"],
                "partner_id": quote["partnerId"],
                "status": quote["status"],
                "total": float(quote["total"]),
                "is_expired": False,
            }
            for quote in quotes
        ]
    }


def _to_quote_view(payload: dict) -> SimpleNamespace:
    lines = [
        SimpleNamespace(
            product_code=line["productCode"],
            description=line["description"],
            quantity=Decimal(str(line["quantity"])),
            unit_price=Decimal(str(line["unitPrice"])),
            discount_percent=Decimal(str(line["discountPercent"])),
            tax_rate=Decimal(str(line["taxRate"])),
            total=Decimal(str(line["total"])),
        )
        for line in payload.get("lines", [])
    ]
    return SimpleNamespace(
        id=payload["id"],
        quote_number=payload["quoteNumber"],
        quote_date=date.fromisoformat(payload["quoteDate"]),
        valid_until=date.fromisoformat(payload["validUntil"]),
        partner_id=payload["partnerId"],
        partner_name=payload.get("partnerName", payload["partnerId"]),
        status=SimpleNamespace(value=payload["status"]),
        subtotal=Decimal(str(payload["subtotal"])),
        total_tax=Decimal(str(payload["totalTax"])),
        total=Decimal(str(payload["total"])),
        notes=payload.get("notes") or "",
        lines=lines,
    )


def _to_partner_view(payload: dict) -> SimpleNamespace:
    return SimpleNamespace(
        id=payload["id"],
        name=payload["name"],
        tax_id=payload["taxId"],
        full_address=", ".join(filter(None, [
            payload.get("addressStreet"),
            payload.get("addressNumber"),
            payload.get("postalCode"),
            payload.get("city"),
            payload.get("province"),
        ])),
    )
