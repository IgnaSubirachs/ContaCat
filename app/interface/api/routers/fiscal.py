from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List

from app.domain.fiscal.services import FiscalYearService
from app.domain.fiscal.entities import FiscalYear, FiscalYearStatus
from app.infrastructure.persistence.fiscal.repositories import SqlAlchemyFiscalYearRepository
from app.domain.auth.dependencies import get_current_active_user, require_role
from app.domain.auth.entities import User, UserRole

from app.interface.api.templates import templates

router = APIRouter(prefix="/fiscal", tags=["fiscal"])


def get_fiscal_service() -> FiscalYearService:
    repository = SqlAlchemyFiscalYearRepository()
    return FiscalYearService(repository)


# Web Routes
@router.get("/", response_class=HTMLResponse)
async def list_fiscal_years(
    request: Request,
    service: FiscalYearService = Depends(get_fiscal_service),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER))
):
    """List all fiscal years."""
    fiscal_years = service.list_all()
    return templates.TemplateResponse("fiscal/list.html", {
        "request": request,
        "fiscal_years": fiscal_years,
        "user": current_user
    })


@router.get("/create", response_class=HTMLResponse)
async def create_fiscal_year_form(
    request: Request,
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Show form to create a new fiscal year."""
    return templates.TemplateResponse("fiscal/create.html", {
        "request": request,
        "user": current_user
    })


@router.post("/create")
async def create_fiscal_year(
    request: Request,
    name: str = Form(...),
    start_date: date = Form(...),
    end_date: date = Form(...),
    service: FiscalYearService = Depends(get_fiscal_service),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Create a new fiscal year."""
    try:
        service.create_fiscal_year(name, start_date, end_date)
        return RedirectResponse(url="/fiscal/", status_code=302)
    except ValueError as e:
        return templates.TemplateResponse("fiscal/create.html", {
            "request": request,
            "error": str(e),
            "user": current_user
        })


@router.post("/{fiscal_year_id}/close")
async def close_fiscal_year(
    fiscal_year_id: int,
    service: FiscalYearService = Depends(get_fiscal_service),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Close a fiscal year."""
    try:
        service.close_fiscal_year(fiscal_year_id)
        return RedirectResponse(url="/fiscal/", status_code=302)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{fiscal_year_id}/reopen")
async def reopen_fiscal_year(
    fiscal_year_id: int,
    service: FiscalYearService = Depends(get_fiscal_service),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Reopen a closed fiscal year."""
    try:
        service.reopen_fiscal_year(fiscal_year_id)
        return RedirectResponse(url="/fiscal/", status_code=302)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# API Routes for JSON responses
@router.get("/api/current")
async def get_current_fiscal_year(
    service: FiscalYearService = Depends(get_fiscal_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get the current open fiscal year."""
    fiscal_year = service.get_current_fiscal_year()
    if not fiscal_year:
        raise HTTPException(status_code=404, detail="No open fiscal year found")
    return {
        "id": fiscal_year.id,
        "name": fiscal_year.name,
        "start_date": fiscal_year.start_date.isoformat(),
        "end_date": fiscal_year.end_date.isoformat(),
        "status": fiscal_year.status.value
    }

# Fical Models
from app.domain.fiscal.services import FiscalModelService
from app.infrastructure.persistence.accounting.repository import SqlAlchemyJournalRepository
from app.infrastructure.persistence.settings.repository import SqlAlchemyCompanySettingsRepository
from app.infrastructure.persistence.hr.repository import SqlAlchemyPayrollRepository
from app.domain.settings.services import SettingsService
from app.infrastructure.db.base import SessionLocal

def get_fiscal_model_service() -> FiscalModelService:
    journal_repo = SqlAlchemyJournalRepository(SessionLocal)
    settings_repo = SqlAlchemyCompanySettingsRepository(SessionLocal)
    payroll_repo = SqlAlchemyPayrollRepository(SessionLocal)
    settings_service = SettingsService(settings_repo)
    return FiscalModelService(journal_repo, settings_service, payroll_repo)

@router.get("/models/303", response_class=HTMLResponse)
async def model_303(
    request: Request,
    year: int = None,
    period: str = None,
    service: FiscalModelService = Depends(get_fiscal_model_service)
):
    """
    Show Model 303.
    If year/period provided, calculate and populate template.
    Else show empty form.
    """
    data = None
    if year and period:
        # Calculate dates
        # T1: Jan-Mar, T2: Apr-Jun...
        # 01...12 for monthly
        # Assume Quarterly for MVP
        quarters = {
            "1T": ((date(year, 1, 1), date(year, 3, 31))),
            "2T": ((date(year, 4, 1), date(year, 6, 30))),
            "3T": ((date(year, 7, 1), date(year, 9, 30))),
            "4T": ((date(year, 10, 1), date(year, 12, 31)))
        }
        
        if period in quarters:
            start_date, end_date = quarters[period]
            data = service.calculate_model_303(year, period, start_date, end_date)
    
    # Get current year for default
    if not year:
        year = date.today().year
    
    return templates.TemplateResponse("fiscal/model303.html", {
        "request": request,
        "data": data,
        "selected_year": year,
        "selected_period": period,
        "periods": ["1T", "2T", "3T", "4T"]
    })

@router.get("/models/111", response_class=HTMLResponse)
async def model_111(
    request: Request,
    year: int = None,
    period: str = None,
    service: FiscalModelService = Depends(get_fiscal_model_service)
):
    """
    Show Model 111 (IRPF).
    """
    data = None
    if year and period:
        quarters = {
            "1T": ((date(year, 1, 1), date(year, 3, 31))),
            "2T": ((date(year, 4, 1), date(year, 6, 30))),
            "3T": ((date(year, 7, 1), date(year, 9, 30))),
            "4T": ((date(year, 10, 1), date(year, 12, 31)))
        }
        
        if period in quarters:
            start_date, end_date = quarters[period]
            data = service.calculate_model_111(year, period, start_date, end_date)
    
    if not year:
        year = date.today().year
    
    return templates.TemplateResponse("fiscal/model111.html", {
        "request": request,
        "data": data,
        "selected_year": year,
        "selected_period": period,
        "periods": ["1T", "2T", "3T", "4T"]
    })
