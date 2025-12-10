from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date

from app.infrastructure.db.base import get_db
from app.domain.assets.services import AssetService
from app.domain.assets.entities import Asset, AssetStatus, DepreciationMethod
from app.infrastructure.persistence.assets.repositories import SqlAlchemyAssetRepository
from app.domain.auth.dependencies import get_current_active_user

router = APIRouter(
    prefix="/assets",
    tags=["assets"],
    dependencies=[Depends(get_current_active_user)]
)

from app.interface.api.templates import templates

from app.infrastructure.persistence.accounting.repository import SqlAlchemyJournalRepository
from app.infrastructure.persistence.accounts.repository import SqlAlchemyAccountRepository
from app.domain.accounting.services import AccountingService

def get_asset_service(db: Session = Depends(get_db)) -> AssetService:
    asset_repository = SqlAlchemyAssetRepository(db)
    account_repository = SqlAlchemyAccountRepository(db)
    journal_repository = SqlAlchemyJournalRepository(lambda: db)
    accounting_service = AccountingService(account_repository, journal_repository)
    return AssetService(asset_repository, accounting_service)


@router.get("/", response_class=HTMLResponse)
async def list_assets(
    request: Request,
    service: AssetService = Depends(get_asset_service)
):
    """List all assets."""
    assets = service.list_assets()
    return templates.TemplateResponse(
        "assets/list.html",
        {"request": request, "assets": assets}
    )

@router.get("/create", response_class=HTMLResponse)
async def create_asset_form(request: Request):
    """Show create asset form."""
    return templates.TemplateResponse(
        "assets/create.html",
        {"request": request, "statuses": AssetStatus, "methods": DepreciationMethod}
    )

@router.post("/create")
async def create_asset(
    code: str = Form(...),
    name: str = Form(...),
    description: str = Form(None),
    purchase_date: str = Form(...),
    purchase_price: float = Form(...),
    useful_life_years: int = Form(...),
    residual_value: float = Form(0.0),
    account_code_asset: str = Form(...),
    account_code_accumulated_depreciation: str = Form(...),
    account_code_depreciation_expense: str = Form(...),
    service: AssetService = Depends(get_asset_service)
):
    """Create a new asset."""
    try:
        asset = Asset(
            code=code,
            name=name,
            description=description,
            purchase_date=date.fromisoformat(purchase_date),
            purchase_price=purchase_price,
            useful_life_years=useful_life_years,
            residual_value=residual_value,
            account_code_asset=account_code_asset,
            account_code_accumulated_depreciation=account_code_accumulated_depreciation,
            account_code_depreciation_expense=account_code_depreciation_expense
        )
        service.create_asset(asset)
        return RedirectResponse(url="/assets", status_code=303)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{asset_id}", response_class=HTMLResponse)
async def view_asset(
    request: Request,
    asset_id: int,
    service: AssetService = Depends(get_asset_service)
):
    """View asset details."""
    try:
        asset = service.get_asset(asset_id)
        return templates.TemplateResponse(
            "assets/details.html",
            {"request": request, "asset": asset}
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Asset not found")

@router.post("/{asset_id}/depreciate")
async def generate_depreciation(
    asset_id: int,
    year: int = Form(...),
    service: AssetService = Depends(get_asset_service)
):
    """Generate depreciation entry for an asset."""
    try:
        service.generate_depreciation_entries(asset_id, year)
        return RedirectResponse(url=f"/assets/{asset_id}", status_code=303)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
