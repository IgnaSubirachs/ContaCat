from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import date
import os

from app.domain.inventory.services import InventoryService
from app.domain.inventory.entities import StockItem, StockMovement
from app.infrastructure.persistence.inventory.repositories import (
    SqlAlchemyStockItemRepository,
    SqlAlchemyStockMovementRepository
)

# Initialize templates
current_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(current_dir, "../../web/templates")
templates = Jinja2Templates(directory=templates_dir)

# Initialize service
item_repo = SqlAlchemyStockItemRepository()
movement_repo = SqlAlchemyStockMovementRepository()
inventory_service = InventoryService(item_repo, movement_repo)

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/", response_class=HTMLResponse)
async def list_items(request: Request):
    """List all stock items."""
    items = inventory_service.list_items()
    return templates.TemplateResponse(
        "inventory/list.html",
        {"request": request, "items": items}
    )


@router.get("/create", response_class=HTMLResponse)
async def create_item_form(request: Request):
    """Show create item form."""
    return templates.TemplateResponse(
        "inventory/create.html",
        {"request": request}
    )


@router.post("/create")
async def create_item(
    code: str = Form(...),
    name: str = Form(...),
    description: str = Form(None),
    unit_price: float = Form(0.0),
    quantity: int = Form(0),
    location: str = Form(None)
):
    """Create a new stock item."""
    try:
        item = StockItem(
            code=code,
            name=name,
            description=description,
            unit_price=unit_price,
            quantity=quantity,
            location=location
        )
        inventory_service.create_item(item)
        return RedirectResponse(url="/inventory", status_code=303)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{item_id}", response_class=HTMLResponse)
async def view_item(request: Request, item_id: str):
    """View item details."""
    item = inventory_service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Article no trobat")
    
    movements = inventory_service.list_movements(item.code)
    return templates.TemplateResponse(
        "inventory/details.html",
        {"request": request, "item": item, "movements": movements}
    )


@router.get("/{item_id}/edit", response_class=HTMLResponse)
async def edit_item_form(request: Request, item_id: str):
    """Show edit item form."""
    item = inventory_service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Article no trobat")
    
    return templates.TemplateResponse(
        "inventory/edit.html",
        {"request": request, "item": item}
    )


@router.post("/{item_id}/edit")
async def update_item(
    item_id: str,
    code: str = Form(...),
    name: str = Form(...),
    description: str = Form(None),
    unit_price: float = Form(0.0),
    location: str = Form(None)
):
    """Update a stock item."""
    try:
        existing = inventory_service.get_item(item_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Article no trobat")
        
        item = StockItem(
            id=item_id,
            code=code,
            name=name,
            description=description,
            unit_price=unit_price,
            quantity=existing.quantity,
            location=location,
            is_active=existing.is_active
        )
        inventory_service.update_item(item)
        return RedirectResponse(url=f"/inventory/{item_id}", status_code=303)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{item_id}/movement")
async def register_movement(
    item_id: str,
    quantity: int = Form(...),
    description: str = Form(None)
):
    """Register a stock movement."""
    try:
        item = inventory_service.get_item(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Article no trobat")
        
        movement = StockMovement(
            stock_item_code=item.code,
            date=date.today(),
            quantity=quantity,
            description=description
        )
        inventory_service.register_movement(movement)
        return RedirectResponse(url=f"/inventory/{item_id}", status_code=303)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{item_id}/delete")
async def delete_item(item_id: str):
    """Delete a stock item."""
    try:
        inventory_service.delete_item(item_id)
        return RedirectResponse(url="/inventory", status_code=303)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
