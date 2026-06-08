from types import SimpleNamespace
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.domain.auth.dependencies import get_current_active_user
from app.infrastructure.java_erp_client import JavaErpClient, JavaErpClientError
from app.interface.api.templates import templates


ACCOUNT_TYPES = ["ASSET", "LIABILITY", "EQUITY", "INCOME", "EXPENSE"]


def get_java_erp_client() -> JavaErpClient:
    return JavaErpClient()


router = APIRouter(
    prefix="/accounts",
    tags=["accounts"],
    dependencies=[Depends(get_current_active_user)],
)


@router.get("/", response_class=HTMLResponse)
async def list_accounts(
    request: Request,
    group: Optional[int] = None,
    client: JavaErpClient = Depends(get_java_erp_client),
):
    try:
        accounts = [_to_account_view(account) for account in client.list_accounts(group)]
    except JavaErpClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return templates.TemplateResponse(
        "accounts/list.html",
        {"request": request, "accounts": accounts},
    )


@router.get("/create", response_class=HTMLResponse)
async def create_account_form(request: Request):
    account_types = [SimpleNamespace(value=account_type) for account_type in ACCOUNT_TYPES]
    return templates.TemplateResponse(
        "accounts/create.html",
        {"request": request, "account_types": account_types},
    )


@router.post("/create")
async def create_account(
    code: str = Form(...),
    name: str = Form(...),
    account_type: str = Form(...),
    group: int = Form(...),
    parent_code: Optional[str] = Form(None),
    client: JavaErpClient = Depends(get_java_erp_client),
):
    try:
        parent_account_id = _find_parent_account_id(client, parent_code)
        client.create_account(code, name, account_type, group, parent_account_id)
        return RedirectResponse(url="/accounts/", status_code=303)
    except JavaErpClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/api/list")
async def api_list_accounts(
    group: Optional[int] = None,
    client: JavaErpClient = Depends(get_java_erp_client),
):
    try:
        return {"accounts": client.list_accounts(group)}
    except JavaErpClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


def _find_parent_account_id(client: JavaErpClient, parent_code: str | None) -> str | None:
    if not parent_code:
        return None

    parent_code = parent_code.strip()
    if not parent_code:
        return None

    accounts = client.list_accounts()
    parent = next((account for account in accounts if account["code"] == parent_code), None)
    if parent is None:
        raise JavaErpClientError(f"No existeix cap compte pare amb codi {parent_code}.")
    return parent["id"]


def _to_account_view(account: dict) -> SimpleNamespace:
    return SimpleNamespace(
        id=account["id"],
        code=account["code"],
        name=account["name"],
        account_type=SimpleNamespace(value=account["accountType"]),
        group=account["group"],
        parent_code=None,
        is_active=account["active"],
    )
