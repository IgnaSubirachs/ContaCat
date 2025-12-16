from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from app.interface.api.templates import templates
from app.infrastructure.persistence.treasury.repository import SqlAlchemyTreasuryRepository
from app.infrastructure.persistence.sales.repository import SqlAlchemySalesInvoiceRepository
from app.domain.treasury.services import TreasuryService

router = APIRouter()

def get_treasury_service():
    from app.infrastructure.db.base import SessionLocal
    treasury_repo = SqlAlchemyTreasuryRepository()
    sales_repo = SqlAlchemySalesInvoiceRepository(SessionLocal)
    
    # Optional: Add accounting service for cash balance
    from app.domain.accounting.services import AccountingService
    from app.infrastructure.persistence.accounts.repository import SqlAlchemyAccountRepository
    from app.infrastructure.persistence.accounting.repository import SqlAlchemyJournalRepository
    account_repo = SqlAlchemyAccountRepository(SessionLocal)
    journal_repo = SqlAlchemyJournalRepository(SessionLocal)
    accounting_service = AccountingService(account_repo, journal_repo)
    
    # Optional: Add payroll repo for expenses
    from app.infrastructure.persistence.hr.repository import SqlAlchemyPayrollRepository
    payroll_repo = SqlAlchemyPayrollRepository(SessionLocal)
    
    return TreasuryService(treasury_repo, sales_repo, accounting_service, payroll_repo)

@router.get("/treasury/cash-flow", response_class=HTMLResponse)
async def cash_flow_forecast(request: Request, days: int = 30):
    service = get_treasury_service()
    forecast = service.get_cash_flow_forecast(days)
    return templates.TemplateResponse(
        "treasury/cash_flow.html",
        {"request": request, "forecast": forecast, "days": days}
    )

@router.get("/treasury/accounts", response_class=HTMLResponse)
async def list_bank_accounts(request: Request):
    service = get_treasury_service()
    accounts = service.list_bank_accounts()
    return templates.TemplateResponse(
        "treasury/accounts_list.html",
        {"request": request, "accounts": accounts}
    )

@router.get("/treasury/accounts/new", response_class=HTMLResponse)
async def new_bank_account(request: Request):
    return templates.TemplateResponse(
        "treasury/account_create.html",
        {"request": request}
    )

@router.post("/treasury/accounts", response_class=HTMLResponse)
async def create_bank_account(
    request: Request,
    name: str = Form(...),
    iban: str = Form(...),
    bic: str = Form(None),
    account_code: str = Form(None)
):
    service = get_treasury_service()
    service.create_bank_account(name, iban, bic, account_code)
    return RedirectResponse(url="/treasury/accounts", status_code=303)

@router.get('/treasury/forecast', response_class=HTMLResponse)
async def treasury_dashboard(request: Request):
    service = get_treasury_service()
    dashboard = service.get_treasury_dashboard()
    return templates.TemplateResponse('treasury/forecast.html', {'request': request, 'dashboard': dashboard})
