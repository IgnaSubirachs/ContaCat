from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
from sqlalchemy.orm import Session

from app.infrastructure.db.database import get_db
from app.domain.auth.dependencies import get_current_user
from app.domain.auth.entities import User
from app.domain.budgets.services import BudgetService
from app.infrastructure.persistence.budgets.repository import SqlAlchemyBudgetRepository
from app.interface.api.templates import templates

router = APIRouter(
    prefix="/budgets",
    tags=["budgets"],
    responses={404: {"description": "Not found"}},
)

def get_budget_service(db: Session = Depends(get_db)) -> BudgetService:
    repo = SqlAlchemyBudgetRepository(db)
    return BudgetService(repo)

@router.get("/", response_class=HTMLResponse)
async def list_budgets(
    request: Request,
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service)
):
    budgets = service.list_budgets()
    return templates.TemplateResponse("budgets/list.html", {
        "request": request,
        "budgets": budgets,
        "user": current_user
    })

@router.get("/create", response_class=HTMLResponse)
async def create_budget_form(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    return templates.TemplateResponse("budgets/create.html", {
        "request": request,
        "user": current_user
    })

@router.post("/create")
async def create_budget(
    request: Request,
    name: str = Form(...),
    year: int = Form(...),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service)
):
    service.create_budget(name, year, description)
    return RedirectResponse(url="/budgets/", status_code=303)

@router.get("/{id}", response_class=HTMLResponse)
async def view_budget(
    id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service)
):
    budget = service.get_budget(id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
        
    return templates.TemplateResponse("budgets/details.html", {
        "request": request,
        "budget": budget,
        "user": current_user
    })

@router.post("/{id}/lines")
async def add_budget_line(
    id: str,
    account_group: str = Form(...),
    amount: float = Form(...),
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service)
):
    updated_budget = service.add_budget_line(id, account_group, amount)
    if not updated_budget:
         raise HTTPException(status_code=404, detail="Budget not found")
    
    return RedirectResponse(url=f"/budgets/{id}", status_code=303)

@router.post("/delete/{id}")
async def delete_budget(
    id: str,
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service)
):
    service.delete_budget(id)
    return RedirectResponse(url="/budgets/", status_code=303)
