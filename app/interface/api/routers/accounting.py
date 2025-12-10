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
from app.interface.api.templates import templates

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


@router.get("/reports/balance-sheet", response_class=HTMLResponse)
async def balance_sheet(request: Request, end_date: str = None):
    """Show balance sheet (Balanç de Situació)."""
    end_date_obj = None
    if end_date:
        try:
            end_date_obj = date.fromisoformat(end_date)
        except ValueError:
            pass
    
    balance_sheet = accounting_service.get_balance_sheet(end_date_obj)
    
    return templates.TemplateResponse(
        "accounting/balance_sheet.html",
        {"request": request, "balance_sheet": balance_sheet}
    )


@router.get("/reports/profit-loss", response_class=HTMLResponse)
async def profit_loss(request: Request, start_date: str = None, end_date: str = None):
    """Show profit and loss statement (Compte de Pèrdues i Guanys)."""
    start_date_obj = None
    end_date_obj = None
    
    if start_date:
        try:
            start_date_obj = date.fromisoformat(start_date)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date_obj = date.fromisoformat(end_date)
        except ValueError:
            pass
    
    profit_loss = accounting_service.get_profit_loss(start_date_obj, end_date_obj)
    
    return templates.TemplateResponse(
        "accounting/profit_loss.html",
        {"request": request, "profit_loss": profit_loss}
    )


# Export endpoints
@router.get("/reports/balance-sheet/export")
async def export_balance_sheet(format: str = "pdf", end_date: str = None):
    """Export balance sheet to PDF or Excel."""
    from fastapi.responses import FileResponse
    from app.domain.accounting.export_utils import ReportExporter
    import tempfile
    
    end_date_obj = None
    if end_date:
        try:
            end_date_obj = date.fromisoformat(end_date)
        except ValueError:
            pass
    
    balance_sheet = accounting_service.get_balance_sheet(end_date_obj)
    
    # Create temporary file
    suffix = ".pdf" if format == "pdf" else ".xlsx"
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    
    try:
        if format == "pdf":
            ReportExporter.export_balance_sheet_to_pdf(balance_sheet, temp_file.name)
            media_type = "application/pdf"
            filename = f"balanc_situacio_{date.today().isoformat()}.pdf"
        else:  # excel
            ReportExporter.export_balance_sheet_to_excel(balance_sheet, temp_file.name)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"balanc_situacio_{date.today().isoformat()}.xlsx"
        
        return FileResponse(
            temp_file.name,
            media_type=media_type,
            filename=filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generant l'exportació: {str(e)}")


@router.get("/reports/profit-loss/export")
async def export_profit_loss(format: str = "pdf", start_date: str = None, end_date: str = None):
    """Export profit & loss statement to PDF or Excel."""
    from fastapi.responses import FileResponse
    from app.domain.accounting.export_utils import ReportExporter
    import tempfile
    
    start_date_obj = None
    end_date_obj = None
    
    if start_date:
        try:
            start_date_obj = date.fromisoformat(start_date)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date_obj = date.fromisoformat(end_date)
        except ValueError:
            pass
    
    profit_loss = accounting_service.get_profit_loss(start_date_obj, end_date_obj)
    
    # Create temporary file
    suffix = ".pdf" if format == "pdf" else ".xlsx"
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    
    try:
        if format == "pdf":
            ReportExporter.export_profit_loss_to_pdf(profit_loss, temp_file.name)
            media_type = "application/pdf"
            filename = f"compte_pyg_{date.today().isoformat()}.pdf"
        else:  # excel
            ReportExporter.export_profit_loss_to_excel(profit_loss, temp_file.name)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"compte_pyg_{date.today().isoformat()}.xlsx"
        
        return FileResponse(
            temp_file.name,
            media_type=media_type,
            filename=filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generant l'exportació: {str(e)}")


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
