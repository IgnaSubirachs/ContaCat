from fastapi import APIRouter, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
from typing import Optional

from app.domain.accounts.services import AccountService
from app.domain.accounts.entities import AccountType
from app.infrastructure.persistence.accounts.repository import SqlAlchemyAccountRepository

# Initialize templates
from app.interface.api.templates import templates

# Initialize service
def get_account_service():
    repo = SqlAlchemyAccountRepository()
    return AccountService(repo)

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("/", response_class=HTMLResponse)
async def list_accounts(request: Request, service: AccountService = Depends(get_account_service)):
    """List all accounts."""
    accounts = service.list_accounts()
    return templates.TemplateResponse(
        "accounts/list.html",
        {"request": request, "accounts": accounts}
    )

@router.get("/create", response_class=HTMLResponse)
async def create_account_form(request: Request):
    """Show create account form."""
    return templates.TemplateResponse(
        "accounts/create.html",
        {"request": request, "account_types": AccountType}
    )

@router.post("/create")
async def create_account(
    code: str = Form(...),
    name: str = Form(...),
    account_type: str = Form(...),
    group: int = Form(...),
    parent_code: Optional[str] = Form(None),
    service: AccountService = Depends(get_account_service)
):
    """Create a new account."""
    try:
        # Convert string to Enum
        try:
            type_enum = AccountType(account_type)
        except ValueError:
            raise ValueError(f"Invalid account type: {account_type}")

        service.create_account(
            code=code,
            name=name,
            account_type=type_enum,
            group=group,
            parent_code=parent_code
        )
        return RedirectResponse(url="/accounts/", status_code=303)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/api/list")
async def api_list_accounts(service: AccountService = Depends(get_account_service)):
    """API endpoint to list accounts as JSON."""
    accounts = service.list_accounts()
    return {
        "accounts": [
            {
                "id": a.id,
                "code": a.code,
                "name": a.name,
                "type": a.account_type.value,
                "group": a.group,
                "parent_code": a.parent_code,
                "is_active": a.is_active
            }
            for a in accounts
        ]
    }
