from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List
import os

from app.domain.partners.services import PartnerService
from app.infrastructure.persistence.partners.repository import SqlAlchemyPartnerRepository

# Initialize templates
current_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(current_dir, "../../web/templates")
templates = Jinja2Templates(directory=templates_dir)

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
        )
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
