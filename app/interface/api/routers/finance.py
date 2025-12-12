from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session

from app.infrastructure.db.database import get_db
from app.domain.auth.dependencies import get_current_user
from app.domain.auth.entities import User
from app.domain.finance.services import FinanceService
from app.infrastructure.persistence.finance.repository import SqlAlchemyLoanRepository
from app.domain.finance.entities import Loan
from app.interface.api.templates import templates
from app.domain.partners.services import PartnerService
from app.infrastructure.persistence.partners.repository import SqlAlchemyPartnerRepository

router = APIRouter(
    prefix="/finance",
    tags=["finance"],
    responses={404: {"description": "Not found"}},
)

def get_finance_service(db: Session = Depends(get_db)) -> FinanceService:
    repo = SqlAlchemyLoanRepository(db)
    return FinanceService(repo)

def get_partner_service(db: Session = Depends(get_db)) -> PartnerService:
    repo = SqlAlchemyPartnerRepository(db)
    return PartnerService(repo)

@router.get("/loans", response_class=HTMLResponse)
async def list_loans(
    request: Request,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service)
):
    loans = service.list_loans()
    return templates.TemplateResponse("finance/loans_list.html", {
        "request": request,
        "loans": loans,
        "user": current_user
    })

@router.get("/loans/create", response_class=HTMLResponse)
async def create_loan_form(
    request: Request,
    current_user: User = Depends(get_current_user),
    partner_service: PartnerService = Depends(get_partner_service)
):
    partners = partner_service.list_partners() # To select lender
    return templates.TemplateResponse("finance/loan_create.html", {
        "request": request,
        "user": current_user,
        "partners": partners
    })

@router.post("/loans/create")
async def create_loan(
    request: Request,
    name: str = Form(...),
    lender_partner_id: str = Form(...),
    principal_amount: float = Form(...),
    interest_rate: float = Form(...),
    start_date: str = Form(...),
    duration_months: int = Form(...),
    
    account_principal_long_term: str = Form(...),
    account_principal_short_term: str = Form(...),
    account_interest_expense: str = Form(...),
    account_bank: str = Form(...),
    
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service)
):
    service.create_loan(
        name=name,
        lender_partner_id=lender_partner_id,
        principal_amount=principal_amount,
        interest_rate=interest_rate,
        start_date=date.fromisoformat(start_date),
        duration_months=duration_months,
        account_principal_long_term=account_principal_long_term,
        account_principal_short_term=account_principal_short_term,
        account_interest_expense=account_interest_expense,
        account_bank=account_bank,
        description=description
    )
    return RedirectResponse(url="/finance/loans", status_code=303)

@router.get("/loans/{id}", response_class=HTMLResponse)
async def view_loan(
    id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service)
):
    loan = service.get_loan(id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
        
    return templates.TemplateResponse("finance/loan_details.html", {
        "request": request,
        "loan": loan,
        "user": current_user
    })

@router.post("/loans/{loan_id}/post-installment/{installment_id}")
async def post_installment(
    loan_id: str,
    installment_id: str,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service)
):
    # In a real scenario, this would call AccountingService to create journal entries.
    # For now, we just mark it as POSTED and simulate a journal entry ID.
    import uuid
    dummy_journal_id = str(uuid.uuid4())
    
    success = service.mark_installment_as_posted(loan_id, installment_id, dummy_journal_id)
    
    if not success:
         raise HTTPException(status_code=404, detail="Installment not found")
    
    return RedirectResponse(url=f"/finance/loans/{loan_id}", status_code=303)
