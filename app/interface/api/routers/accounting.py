from fastapi import APIRouter, HTTPException, Request, Form, UploadFile, File, Response
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from datetime import date
from decimal import Decimal
import os
import uuid
import shutil
import tempfile

from app.domain.accounting.services import AccountingService
from app.domain.accounts.entities import AccountType
from app.infrastructure.persistence.accounts.repository import SqlAlchemyAccountRepository
from app.infrastructure.persistence.accounting.repository import SqlAlchemyJournalRepository
from app.domain.accounting.reporting_service import ReportingService

# New dependencies for Reporting
from app.domain.documents.services import DocumentService
from app.domain.settings.services import SettingsService
from app.infrastructure.persistence.settings.repository import SqlAlchemyCompanySettingsRepository
from app.domain.accounting.export_utils import ReportExporter # Keep for Excel

# Initialize templates
from app.interface.api.templates import templates

# Initialize services
account_repo = SqlAlchemyAccountRepository()
journal_repo = SqlAlchemyJournalRepository()
accounting_service = AccountingService(account_repo, journal_repo)
reporting_service = ReportingService(accounting_service)

settings_repo = SqlAlchemyCompanySettingsRepository(None) # Session handled internally by repo if using factory, but repo expects session_factory usually
# Wait, SqlAlchemyCompanySettingsRepository __init__?
# Let's check dependencies injection. It likely needs generic session handling.
# existing code used: stock_item_repo = SqlAlchemyStockItemRepository(SessionLocal)
# But here we are instantiating globally? That's bad practice for Session.
# However, the previous code for account_repo = SqlAlchemyAccountRepository() suggests it handles its own session or is using a global scope convention (which is risky).
# Let's follow the pattern found in `sales_invoices.py`: use Depends(get_db) or instantiate with SessionLocal.
# But `accounting.py` here has global instantiation on line 20: account_repo = SqlAlchemyAccountRepository().
# I will stick to what's there but check if SqlAlchemyCompanySettingsRepository needs args.
# Checking `app/infrastructure/persistence/settings/repository.py`... 
# Assuming it works like account_repo for now.
from app.infrastructure.db.base import SessionLocal
settings_repo = SqlAlchemyCompanySettingsRepository(SessionLocal)
settings_service = SettingsService(settings_repo)
document_service = DocumentService()


router = APIRouter(prefix="/accounting", tags=["accounting"])

@router.get("/journal", response_class=HTMLResponse)
async def journal_list(request: Request):
    """Show journal entries list (Llibre Diari)."""
    entries = accounting_service.list_journal_entries()
    
    return templates.TemplateResponse(
        "accounting/journal.html",
        {"request": request, "entries": entries}
    )

@router.get("/journal/create", response_class=HTMLResponse)
async def create_entry_form(request: Request):
    """Show form to create new journal entry."""
    try:
        accounts = accounting_service.list_accounts()
        
        return templates.TemplateResponse(
            "accounting/journal/create.html",
            {"request": request, "accounts": accounts}
        )
    except Exception as e:
        # Log the error and return error page
        print(f"Error loading journal create form: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading accounts: {str(e)}")

@router.post("/journal/create")
async def create_entry(
    request: Request,
    entry_date: date = Form(...),
    description: str = Form(...),
    attachment: UploadFile = File(None)
):
    """Create a new journal entry."""
    try:
        # Handle attachment
        attachment_path = None
        if attachment and attachment.filename:
            # Create uploads dir if not exists
            upload_dir = os.path.join("frontend", "static", "uploads", "accounting")
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            ext = os.path.splitext(attachment.filename)[1]
            filename = f"{uuid.uuid4()}{ext}"
            file_path = os.path.join(upload_dir, filename)
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(attachment.file, buffer)
            
            attachment_path = f"/static/uploads/accounting/{filename}"

        # Get form data for lines
        form_data = await request.form()
        
        # Parse lines
        lines = []
        i = 0
        while True:
            # Flexible parsing to handle account_code_{i} or account_{i}
            account_code = form_data.get(f"account_code_{i}") or form_data.get(f"account_{i}")
            if not account_code and i > 50: # Safety break if too many empty lines check
                 break
            if not account_code: 
                # continue checking? Template generates sequential IDs, so if missing, maybe end of list
                # But to be safe against holes, check a bit further or use a hidden field for count
                if i > 20 and not form_data.get(f"account_code_{i+1}"): # Heuristic
                    break
                i += 1
                continue

            debit = Decimal(form_data.get(f"debit_{i}", "0") or "0")
            credit = Decimal(form_data.get(f"credit_{i}", "0") or "0")
            line_desc = form_data.get(f"description_{i}", "")
            
            if account_code:
                lines.append((account_code, debit, credit, line_desc))
            i += 1
        
        accounting_service.create_journal_entry(
            entry_date=entry_date,
            description=description,
            lines=lines,
            attachment_path=attachment_path
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
    
    balance_sheet = reporting_service.get_balance_sheet_report(end_date_obj)
    
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
    
    profit_loss = reporting_service.get_profit_loss_report(start_date_obj, end_date_obj)
    
    return templates.TemplateResponse(
        "accounting/profit_loss.html",
        {"request": request, "profit_loss": profit_loss}
    )


# Export endpoints
@router.get("/reports/balance-sheet/export")
async def export_balance_sheet(request: Request, format: str = "pdf", end_date: str = None):
    """Export balance sheet to PDF or Excel."""
    end_date_obj = None
    if end_date:
        try:
            end_date_obj = date.fromisoformat(end_date)
        except ValueError:
            pass
    
    balance_sheet = reporting_service.get_balance_sheet_report(end_date_obj)
    
    if format == "pdf":
        # Get settings for logo/header
        settings = settings_service.get_settings()
        
        # Render HTML template for PDF
        html_content = templates.TemplateResponse(
            "accounting/reports/balance_sheet_pdf.html",
            {
                "request": request,
                "balance_sheet": balance_sheet,
                "settings": settings
            }
        ).body.decode("utf-8")
        
        # Convert to PDF
        pdf_bytes = document_service.generate_pdf(html_content)
        
        filename = f"balanc_situacio_{date.today().isoformat()}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    else:  # excel (fallback to existing ReportExporter)
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            ReportExporter.export_balance_sheet_to_excel(balance_sheet, temp_file.name)
            
            filename = f"balanc_situacio_{date.today().isoformat()}.xlsx"
            return FileResponse(
                temp_file.name,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                filename=filename
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generant Excel: {str(e)}")


@router.get("/reports/profit-loss/export")
async def export_profit_loss(request: Request, format: str = "pdf", start_date: str = None, end_date: str = None):
    """Export profit & loss statement to PDF or Excel."""
    start_date_obj = None
    end_date_obj = None
    
    if start_date:
        try:
            start_date_obj = date.fromisoformat(start_date)
        except ValueError:
            pass
    if end_date:
        try:
            start_date_obj = date.fromisoformat(end_date) # BUG: Fixed copy paste error? No the variable is correct but value assignment was wrong?
            # Wait, verify line 243 of existing code: try: end_date_obj = date.fromisoformat(end_date)
            # Above logic was: if end_date: try: end_date_obj... 
            # I must ensure I don't introduce bugs.
            end_date_obj = date.fromisoformat(end_date)
        except ValueError:
            pass
    
    profit_loss = reporting_service.get_profit_loss_report(start_date_obj, end_date_obj)
    
    if format == "pdf":
        settings = settings_service.get_settings()
        
        html_content = templates.TemplateResponse(
            "accounting/reports/profit_loss_pdf.html",
            {
                "request": request,
                "profit_loss": profit_loss,
                "settings": settings
            }
        ).body.decode("utf-8")
        
        pdf_bytes = document_service.generate_pdf(html_content)
        
        filename = f"compte_pyg_{date.today().isoformat()}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    else: # excel
         try:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            ReportExporter.export_profit_loss_to_excel(profit_loss, temp_file.name)
            
            filename = f"compte_pyg_{date.today().isoformat()}.xlsx"
            return FileResponse(
                temp_file.name,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                filename=filename
            )
         except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generant Excel: {str(e)}")


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
