from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.domain.auth.dependencies import get_current_user_or_redirect, require_role
from app.domain.auth.entities import User, UserRole
from app.infrastructure.java_erp_client import JavaErpClient, JavaErpClientError
from app.interface.api.templates import templates

router = APIRouter(prefix="/admin/module-licenses", tags=["module-licenses"])


def get_java_erp_client() -> JavaErpClient:
    return JavaErpClient()


@router.get("/", response_class=HTMLResponse, dependencies=[Depends(require_role(UserRole.ADMIN))])
async def module_licenses_page(
    request: Request,
    company_id: str | None = None,
    current_user: Optional[User] = Depends(get_current_user_or_redirect),
    client: JavaErpClient = Depends(get_java_erp_client),
):
    if current_user is None:
        return RedirectResponse(url="/auth/login-page", status_code=302)

    error_message = None
    companies: list[dict] = []
    selected_company_id = company_id
    grouped_modules: dict[str, list[dict]] = {}

    try:
        companies = client.list_companies()
        if companies:
            selected_company_id = selected_company_id or companies[0]["id"]
            licenses = client.list_company_module_licenses(selected_company_id)
            for module in licenses:
                grouped_modules.setdefault(module["category"], []).append(module)
    except JavaErpClientError as exc:
        error_message = str(exc)

    return templates.TemplateResponse(
        "admin/module_licenses.html",
        {
            "request": request,
            "user": current_user,
            "companies": companies,
            "selected_company_id": selected_company_id,
            "grouped_modules": grouped_modules,
            "error_message": error_message,
        },
    )


@router.post("/update", dependencies=[Depends(require_role(UserRole.ADMIN))])
async def update_module_license(
    company_id: str = Form(...),
    module_key: str = Form(...),
    enabled: str = Form(...),
    starts_at: str = Form(""),
    expires_at: str = Form(""),
    client: JavaErpClient = Depends(get_java_erp_client),
):
    parsed_starts_at = date.fromisoformat(starts_at) if starts_at else None
    parsed_expires_at = date.fromisoformat(expires_at) if expires_at else None
    client.update_company_module_license(
        module_key=module_key,
        enabled=enabled == "true",
        company_id=company_id,
        starts_at=parsed_starts_at,
        expires_at=parsed_expires_at,
    )
    return RedirectResponse(url=f"/admin/module-licenses/?company_id={company_id}", status_code=303)
