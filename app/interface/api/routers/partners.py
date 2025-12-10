from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os

from app.domain.partners.services import PartnerService
from app.infrastructure.persistence.partners.repository import SqlAlchemyPartnerRepository

# Initialize templates
from app.interface.api.templates import templates

# Initialize service
partner_repo = SqlAlchemyPartnerRepository()
partner_service = PartnerService(partner_repo)

router = APIRouter(prefix="/partners", tags=["partners"])


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
async def create_partner(
    name: str = Form(...),
    tax_id: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    is_supplier: bool = Form(False),
    is_customer: bool = Form(False),
    # Fiscal fields (simplified for MVP)
    address_street: str = Form(""),
    postal_code: str = Form(""),
    city: str = Form(""),
    iban: str = Form(""),
):
    """Create a new partner."""
    try:
        partner_service.create_partner(
            name=name,
            tax_id=tax_id,
            email=email,
            phone=phone,
            is_supplier=is_supplier,
            is_customer=is_customer,
            address_street=address_street,
            postal_code=postal_code,
            city=city,
            iban=iban,
        )
        return RedirectResponse(url="/partners/", status_code=303)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


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
async def edit_partner(
    partner_id: str,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    is_supplier: bool = Form(False),
    is_customer: bool = Form(False),
    address_street: str = Form(""),
    postal_code: str = Form(""),
    city: str = Form(""),
    iban: str = Form(""),
):
    """Update a partner."""
    try:
        partner_service.update_partner(
            partner_id=partner_id,
            name=name,
            email=email,
            phone=phone,
            is_supplier=is_supplier,
            is_customer=is_customer,
            address_street=address_street,
            postal_code=postal_code,
            city=city,
            iban=iban,
        )
        return RedirectResponse(url="/partners/", status_code=303)
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
