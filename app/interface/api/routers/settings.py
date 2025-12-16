from fastapi import APIRouter, Request, Form, Depends, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional
from app.interface.api.templates import templates
from app.infrastructure.db.base import SessionLocal
from app.domain.settings.services import SettingsService
from app.domain.settings.entities import CompanySettings
from app.infrastructure.persistence.settings.repository import SqlAlchemyCompanySettingsRepository
from app.domain.auth.dependencies import get_current_user_or_redirect
from app.domain.auth.entities import User

router = APIRouter(prefix="/settings", tags=["settings"])

def get_settings_service():
    repo = SqlAlchemyCompanySettingsRepository(SessionLocal)
    return SettingsService(repo)

@router.get("/", response_class=HTMLResponse)
async def settings_form(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_or_redirect)
):
    """Show settings form."""
    if current_user is None:
        return RedirectResponse(url="/auth/login-page", status_code=302)
        
    service = get_settings_service()
    settings = service.get_settings_or_default()
    
    return templates.TemplateResponse("settings/edit.html", {
        "request": request,
        "user": current_user,
        "settings": settings
    })

@router.post("/update")
async def update_settings(
    name: str = Form(...),
    tax_id: str = Form(...),
    address_street: str = Form(""),
    address_city: str = Form(""),
    address_zip: str = Form(""),
    address_province: str = Form(""),
    email: str = Form(""),
    phone: str = Form(""),
    website: str = Form(""),
    smtp_host: str = Form(""),
    smtp_port: int = Form(587),
    smtp_user: str = Form(""),
    smtp_password: str = Form(""),
    smtp_from_email: str = Form(""),
    smtp_from_name: str = Form(""),
    smtp_use_tls: str = Form(None),
    sii_enabled: str = Form(None),
    sii_test_mode: str = Form(None),
    sii_certificate_path: str = Form(""),
    sii_certificate_password: str = Form(""),
    logo: UploadFile = File(None)
):
    """Update settings."""
    service = get_settings_service()
    
    # Handle logo upload (simplified for now: save to static/uploads/logo or generic)
    logo_url = None
    if logo and logo.filename:
        # Save logic here? Or keep previous url.
        # For MVP, assume simplistic handling or skip logo file persistence implementation detail for this turn
        # Actually I should implement it:
        import os
        import shutil
        upload_dir = "frontend/static/uploads/company"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = f"{upload_dir}/logo.png" # Force name for simplicity or use timestamp
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(logo.file, buffer)
        logo_url = "/static/uploads/company/logo.png"
    
    # Needs to handle "keep existing logo if no new one uploaded"
    current_settings = service.get_settings()
    if not logo_url and current_settings and current_settings.logo_url:
        logo_url = current_settings.logo_url

    new_settings = CompanySettings(
        id=current_settings.id if current_settings else None, # Preserve ID or let init generate new (but logic handles update via Singleton Check)
        name=name,
        tax_id=tax_id,
        address_street=address_street,
        address_city=address_city,
        address_zip=address_zip,
        address_province=address_province,
        email=email,
        phone=phone,
        website=website,
        logo_url=logo_url,
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_user=smtp_user,
        smtp_password=smtp_password,
        smtp_from_email=smtp_from_email,
        smtp_from_name=smtp_from_name,
        smtp_use_tls=bool(smtp_use_tls),
        sii_enabled=bool(sii_enabled),
        sii_test_mode=bool(sii_test_mode),
        sii_certificate_path=sii_certificate_path,
        sii_certificate_password=sii_certificate_password
    )
    
    service.save_settings(new_settings)
    
    return RedirectResponse(url="/settings", status_code=303)
