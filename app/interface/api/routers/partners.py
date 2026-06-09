from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
from datetime import date

from app.domain.partners.services import PartnerService
from app.domain.auth.dependencies import get_current_active_user
from app.infrastructure.persistence.partners.repository import SqlAlchemyPartnerRepository

# Initialize templates
from app.interface.api.templates import templates

# Initialize service
partner_repo = SqlAlchemyPartnerRepository()
partner_service = PartnerService(partner_repo)


def _partner_payload(form, include_tax_id: bool = True) -> dict:
    text_fields = (
        "name", "email", "phone", "document_type", "address_street",
        "address_number", "address_floor", "postal_code", "city", "province",
        "country", "vat_regime", "eu_vat_number", "iban", "payment_method",
        "trade_name", "contact_person", "mobile", "website", "customer_code",
        "supplier_code", "relationship_status", "sales_representative",
        "price_list", "customer_account", "supplier_account", "bank_name",
        "bank_account_holder", "swift_bic", "contract_summary", "accrual_notes",
        "internal_notes",
    )
    payload = {field: str(form.get(field, "")).strip() for field in text_fields}
    if include_tax_id:
        payload["tax_id"] = str(form.get("tax_id", "")).strip()
    payload["is_supplier"] = "is_supplier" in form
    payload["is_customer"] = "is_customer" in form
    payload["is_intra_eu"] = "is_intra_eu" in form
    payload["payment_days"] = int(form.get("payment_days") or 0)
    payload["payment_day"] = int(form.get("payment_day") or 0)
    payload["default_discount"] = float(form.get("default_discount") or 0)
    payload["credit_limit"] = float(form.get("credit_limit") or 0)
    relationship_since = str(form.get("relationship_since", "")).strip()
    payload["relationship_since"] = date.fromisoformat(relationship_since) if relationship_since else None
    return payload

router = APIRouter(
    prefix="/partners",
    tags=["partners"],
    dependencies=[Depends(get_current_active_user)]
)


@router.get("/", response_class=HTMLResponse)
async def list_partners(request: Request):
    """List all partners."""
    partners = partner_service.list_all_partners()
    return templates.TemplateResponse(
        "partners/list.html",
        {"request": request, "partners": partners}
    )


@router.get("/create", response_class=HTMLResponse)
async def create_partner_form(request: Request):
    """Show create partner form."""
    return templates.TemplateResponse(
        "partners/create.html",
        {"request": request}
    )


@router.post("/create")
async def create_partner(request: Request):
    """Create a new partner."""
    try:
        partner_service.create_partner(**_partner_payload(await request.form()))
        return RedirectResponse(url="/partners/", status_code=303)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/view/{partner_id}", response_class=HTMLResponse)
async def view_partner(request: Request, partner_id: str):
    partner = partner_service.get_partner_by_id(partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="Partner no trobat")
    return templates.TemplateResponse(
        "partners/detail.html",
        {"request": request, "partner": partner},
    )


@router.get("/edit/{partner_id}", response_class=HTMLResponse)
async def edit_partner_form(request: Request, partner_id: str):
    """Show edit partner form."""
    partner = partner_service.get_partner_by_id(partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="Partner no trobat")
    
    return templates.TemplateResponse(
        "partners/edit.html",
        {"request": request, "partner": partner}
    )


@router.post("/edit/{partner_id}")
async def edit_partner(request: Request, partner_id: str):
    """Update a partner."""
    try:
        partner_service.update_partner(
            partner_id=partner_id,
            **_partner_payload(await request.form(), include_tax_id=False),
        )
        return RedirectResponse(url=f"/partners/view/{partner_id}", status_code=303)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/delete/{partner_id}")
async def delete_partner(partner_id: str):
    """Delete a partner."""
    try:
        partner_service.delete_partner(partner_id)
        return RedirectResponse(url="/partners/", status_code=303)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# JSON API endpoints
@router.get("/api/list")
async def api_list_partners():
    """API endpoint to list all partners as JSON."""
    partners = partner_service.list_all_partners()
    return {
        "partners": [
            {
                "id": p.id,
                "name": p.name,
                "tax_id": p.tax_id,
                "email": p.email,
                "phone": p.phone,
                "is_supplier": p.is_supplier,
                "is_customer": p.is_customer,
            }
            for p in partners
        ]
    }
