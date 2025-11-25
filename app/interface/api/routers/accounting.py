from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import date
from decimal import Decimal
import os

from app.domain.accounting.services import AccountingService
from app.domain.accounts.entities import AccountType
from app.infrastructure.persistence.accounts.repository import SqlAlchemyAccountRepository
from app.infrastructure.persistence.accounting.repository import SqlAlchemyJournalRepository

# Initialize templates
current_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(current_dir, "../../web/templates")
templates = Jinja2Templates(directory=templates_dir)

# Initialize service
account_repo = SqlAlchemyAccountRepository()
journal_repo = SqlAlchemyJournalRepository()
accounting_service = AccountingService(account_repo, journal_repo)

router = APIRouter(prefix="/accounting", tags=["accounting"])


# Chart of Accounts
@router.get("/", response_class=HTMLResponse)
async def accounting_home(request: Request):
    """Accounting home page."""
    return templates.TemplateResponse(
        "accounting/home.html",
        {"request": request}
    )


@router.get("/accounts", response_class=HTMLResponse)
async def list_accounts(request: Request, group: int = None):
    """List chart of accounts."""
    if group:
        accounts = accounting_service.list_accounts_by_group(group)
    else:
        accounts = accounting_service.list_accounts()
    
    return templates.TemplateResponse(
        "accounting/accounts.html",
        {"request": request, "accounts": accounts, "selected_group": group}
    )


@router.get("/accounts/create", response_class=HTMLResponse)
async def create_account_form(request: Request):
    """Show create account form."""
    return templates.TemplateResponse(
        "accounting/account_form.html",
        {"request": request, "account_types": AccountType}
    )


@router.post("/accounts/create")
async def create_account(
    code: str = Form(...),
    name: str = Form(...),
    account_type: str = Form(...),
    group: int = Form(...),
):
    """Create a new account."""
    try:
        accounting_service.create_account(
            code=code,
            name=name,
            account_type=AccountType(account_type),
            group=group
        )
        return RedirectResponse(url="/accounting/accounts", status_code=303)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Journal Entries
@router.get("/journal", response_class=HTMLResponse)
async def list_journal(request: Request):
    """List journal entries (Llibre Diari)."""
    entries = accounting_service.list_journal_entries()
    return templates.TemplateResponse(
        "accounting/journal.html",
        {"request": request, "entries": entries}
    )


@router.get("/journal/create", response_class=HTMLResponse)
async def create_entry_form(request: Request):
    """Show create journal entry form."""
    accounts = accounting_service.list_accounts()
    return templates.TemplateResponse(
        "accounting/entry_form.html",
        {"request": request, "accounts": accounts}
    )


@router.post("/journal/create")
async def create_entry(
    request: Request,
    entry_date: date = Form(...),
    description: str = Form(...),
):
    """Create a new journal entry."""
    try:
        # Get form data for lines
        form_data = await request.form()
        
        # Parse lines
        lines = []
        i = 0
        while f"account_{i}" in form_data:
            account_code = form_data[f"account_{i}"]
            debit = Decimal(form_data.get(f"debit_{i}", "0") or "0")
            credit = Decimal(form_data.get(f"credit_{i}", "0") or "0")
            line_desc = form_data.get(f"line_desc_{i}", "")
            
            if account_code:
                lines.append((account_code, debit, credit, line_desc))
            i += 1
        
        accounting_service.create_journal_entry(
            entry_date=entry_date,
            description=description,
            lines=lines
        )
        return RedirectResponse(url="/accounting/journal", status_code=303)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/journal/{entry_id}/post")
async def post_entry(entry_id: str):
    """Post a journal entry."""
    try:
        accounting_service.post_journal_entry(entry_id)
        return RedirectResponse(url="/accounting/journal", status_code=303)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Reports
@router.get("/ledger/{account_code}", response_class=HTMLResponse)
async def account_ledger(request: Request, account_code: str):
    """Show account ledger (Llibre Major)."""
    account = accounting_service.get_account(account_code)
    if not account:
        raise HTTPException(status_code=404, detail="Compte no trobat")
    
    balance = accounting_service.get_account_balance(account_code)
    entries = accounting_service.list_journal_entries()
    
    # Filter entries with this account
    relevant_entries = []
    for entry in entries:
        for line in entry.lines:
            if line.account_code == account_code:
                relevant_entries.append(entry)
                break
    
    return templates.TemplateResponse(
        "accounting/ledger.html",
        {
            "request": request,
            "account": account,
            "balance": balance,
            "entries": relevant_entries
        }
    )


@router.get("/reports/trial-balance", response_class=HTMLResponse)
async def trial_balance(request: Request):
    """Show trial balance (Balanç de Comprovació)."""
    trial_balance = accounting_service.get_trial_balance()
    
    return templates.TemplateResponse(
        "accounting/trial_balance.html",
        {"request": request, "trial_balance": trial_balance}
    )


# JSON API
@router.get("/api/accounts")
async def api_list_accounts():
    """API endpoint to list accounts."""
    accounts = accounting_service.list_accounts()
    return {
        "accounts": [
            {
                "code": a.code,
                "name": a.name,
                "type": a.account_type.value,
                "group": a.group
            }
            for a in accounts
        ]
    }
