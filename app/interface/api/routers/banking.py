from fastapi import APIRouter, Depends, HTTPException, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session

from app.infrastructure.db.database import get_db
from app.domain.auth.dependencies import get_current_user
from app.domain.auth.entities import User
from app.domain.banking.services import BankingService
from app.infrastructure.persistence.banking.repository import SqlAlchemyBankStatementRepository
from app.interface.api.templates import templates

router = APIRouter(
    prefix="/banking",
    tags=["banking"],
    responses={404: {"description": "Not found"}},
)

def get_banking_service(db: Session = Depends(get_db)) -> BankingService:
    repo = SqlAlchemyBankStatementRepository(db)
    return BankingService(repo)

@router.get("/", response_class=HTMLResponse)
async def list_statements(
    request: Request,
    current_user: User = Depends(get_current_user),
    service: BankingService = Depends(get_banking_service)
):
    statements = service.list_statements()
    return templates.TemplateResponse("banking/list.html", {
        "request": request,
        "statements": statements,
        "user": current_user
    })

@router.get("/upload", response_class=HTMLResponse)
async def upload_form(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    return templates.TemplateResponse("banking/upload.html", {
        "request": request,
        "user": current_user
    })

@router.post("/upload")
async def upload_statement(
    request: Request,
    file: UploadFile = File(...),
    account_id: str = Form(...), # Just a string like "572000" or BankAccount ID
    current_user: User = Depends(get_current_user),
    service: BankingService = Depends(get_banking_service)
):
    content = await file.read()
    service.upload_statement(account_id, file.filename, content)
    return RedirectResponse(url="/banking/", status_code=303)

@router.get("/{id}/reconcile", response_class=HTMLResponse)
async def reconcile_view(
    id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    service: BankingService = Depends(get_banking_service)
):
    statement = service.get_statement(id)
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")
        
    return templates.TemplateResponse("banking/reconcile.html", {
        "request": request,
        "statement": statement,
        "user": current_user
    })

@router.post("/{id}/match/{line_id}")
async def match_line(
    id: str,
    line_id: str,
    journal_entry_id: str = Form(...), # Manual input or selected from list
    current_user: User = Depends(get_current_user),
    service: BankingService = Depends(get_banking_service)
):
    # In a real app, strict validation of journal_entry_id would be here
    service.reconcile_line(id, line_id, journal_entry_id)
    return RedirectResponse(url=f"/banking/{id}/reconcile", status_code=303)
