from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request, Form
from typing import List, Optional
from datetime import date, timedelta
from decimal import Decimal

from app.infrastructure.db.base import SessionLocal
from app.domain.sales.services import QuoteService
from app.domain.sales.entities import QuoteStatus
from app.infrastructure.persistence.sales.repository import SqlAlchemyQuoteRepository
from app.infrastructure.persistence.partners.repository import SqlAlchemyPartnerRepository


router = APIRouter(prefix="/quotes", tags=["quotes"])
templates = Jinja2Templates(directory="app/interface/web/templates")


def get_quote_service():
    """Dependency to get QuoteService instance."""
    session = SessionLocal()
    try:
        quote_repo = SqlAlchemyQuoteRepository(session)
        partner_repo = SqlAlchemyPartnerRepository(session)
        return QuoteService(quote_repo, partner_repo)
    finally:
        pass  # Session will be closed after request


@router.get("/", response_class=HTMLResponse)
async def list_quotes(request: Request, status: Optional[str] = None):
    """List all quotes."""
    service = get_quote_service()
    
    if status:
        try:
            status_enum = QuoteStatus[status.upper()]
            quotes = service.list_quotes(status=status_enum)
        except KeyError:
            quotes = service.list_quotes()
    else:
        quotes = service.list_quotes()
    
    return templates.TemplateResponse("quotes/list.html", {
        "request": request,
        "quotes": quotes,
        "current_status": status
    })


@router.get("/create", response_class=HTMLResponse)
async def create_quote_form(request: Request):
    """Show create quote form."""
    # Get partners for dropdown
    session = SessionLocal()
    partner_repo = SqlAlchemyPartnerRepository(session)
    partners = partner_repo.list_all()
    customers = [p for p in partners if p.is_customer]
    session.close()
    
    return templates.TemplateResponse("quotes/create.html", {
        "request": request,
        "customers": customers
    })


@router.post("/create")
async def create_quote(
    partner_id: str = Form(...),
    quote_date: str = Form(...),
    valid_days: int = Form(30),
    notes: str = Form(""),
    # Lines will be handled via JavaScript/JSON in real implementation
    # For now, we'll accept a simple format
):
    """Create a new quote."""
    service = get_quote_service()
    
    try:
        quote_date_obj = date.fromisoformat(quote_date)
        
        # For now, create with empty lines (will be added via edit)
        quote = service.create_quote(
            partner_id=partner_id,
            quote_date=quote_date_obj,
            valid_days=valid_days,
            lines=[],
            notes=notes
        )
        
        return RedirectResponse(url=f"/quotes/{quote.id}", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{quote_id}", response_class=HTMLResponse)
async def view_quote(request: Request, quote_id: str):
    """View quote details."""
    service = get_quote_service()
    quote = service.get_quote(quote_id)
    
    if not quote:
        raise HTTPException(status_code=404, detail="Pressupost no trobat")
    
    # Get partner details
    session = SessionLocal()
    partner_repo = SqlAlchemyPartnerRepository(session)
    partner = partner_repo.find_by_id(quote.partner_id)
    session.close()
    
    return templates.TemplateResponse("quotes/view.html", {
        "request": request,
        "quote": quote,
        "partner": partner
    })


@router.post("/{quote_id}/send")
async def send_quote(quote_id: str):
    """Send a quote."""
    service = get_quote_service()
    
    try:
        quote = service.send_quote(quote_id)
        return RedirectResponse(url=f"/quotes/{quote.id}", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{quote_id}/accept")
async def accept_quote(quote_id: str):
    """Accept a quote."""
    service = get_quote_service()
    
    try:
        quote = service.accept_quote(quote_id)
        return RedirectResponse(url=f"/quotes/{quote.id}", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{quote_id}/reject")
async def reject_quote(quote_id: str):
    """Reject a quote."""
    service = get_quote_service()
    
    try:
        quote = service.reject_quote(quote_id)
        return RedirectResponse(url=f"/quotes/{quote.id}", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{quote_id}/delete")
async def delete_quote(quote_id: str):
    """Delete a quote."""
    service = get_quote_service()
    
    try:
        service.delete_quote(quote_id)
        return RedirectResponse(url="/quotes/", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# API endpoints (JSON)
@router.get("/api/list")
async def api_list_quotes(status: Optional[str] = None):
    """API endpoint to list quotes as JSON."""
    service = get_quote_service()
    
    if status:
        try:
            status_enum = QuoteStatus[status.upper()]
            quotes = service.list_quotes(status=status_enum)
        except KeyError:
            quotes = service.list_quotes()
    else:
        quotes = service.list_quotes()
    
    return {
        "quotes": [
            {
                "id": q.id,
                "quote_number": q.quote_number,
                "quote_date": q.quote_date.isoformat(),
                "valid_until": q.valid_until.isoformat(),
                "partner_id": q.partner_id,
                "status": q.status.value,
                "total": float(q.total),
                "is_expired": q.is_expired
            }
            for q in quotes
        ]
    }
