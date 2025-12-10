from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional
import os

from app.interface.api.routers import partners
from app.interface.api.routers import employees
from app.interface.api.routers import accounting
from app.interface.api.routers import accounts
from app.interface.api.routers import quotes
from app.interface.api.routers import sales_orders
from app.interface.api.routers import sales_invoices
from app.interface.api.routers import auth
from app.interface.api.routers import assets
from app.interface.api.routers import inventory
from app.interface.api.routers import fiscal
from app.interface.api.routers import analytics

from app.domain.auth.dependencies import get_current_user_or_redirect, can_access_module
from app.domain.auth.entities import User

app = FastAPI(title="ContaCAT", description="ERP Modular amb DDD", version="2.0.0")

# Determine paths relative to this file
# app is at c:\ERP\app\interface\api\main.py
# static is at c:\ERP\frontend\static
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
static_dir = os.path.join(project_root, "frontend/static")

# Mount static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Import centralized templates
from app.interface.api.templates import templates

# Include routers
app.include_router(partners.router)
app.include_router(employees.router)
app.include_router(accounting.router)
app.include_router(accounts.router)
app.include_router(quotes.router)
app.include_router(sales_orders.router)
app.include_router(sales_invoices.router)
app.include_router(auth.router)
app.include_router(assets.router)
app.include_router(inventory.router)
app.include_router(fiscal.router)
app.include_router(analytics.router)



@app.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_or_redirect)
):
    """Home page with navigation to all modules (requires login)."""
    if current_user is None:
        return RedirectResponse(url="/auth/login-page", status_code=302)
    
    # Build list of accessible modules
    modules = []
    module_list = [
        {"id": "partners", "name": "Partners", "desc": "Clients i Proveïdors", "url": "/partners/", "icon": "partners.png"},
        {"id": "employees", "name": "RRHH", "desc": "Empleats i Nòmines", "url": "/employees/", "icon": "hr.png"},
        {"id": "accounts", "name": "Comptes", "desc": "Pla Comptable", "url": "/accounts/", "icon": "accounting.png"},
        {"id": "accounting", "name": "Comptabilitat", "desc": "Gestió Financera", "url": "/accounting/", "icon": "accounting.png"},
        {"id": "fiscal", "name": "Exercicis", "desc": "Anys Fiscals", "url": "/fiscal/", "icon": "accounting.png"},
        {"id": "assets", "name": "Actius Fixos", "desc": "Gestió d'Immobilitzat", "url": "/assets/", "icon": "accounting.png"},
        {"id": "quotes", "name": "Pressupostos", "desc": "Gestió de Quotes", "url": "/quotes/", "icon": "sales.png"},
        {"id": "sales_orders", "name": "Comandes", "desc": "Sales Orders", "url": "/sales/orders/", "icon": "sales.png"},
        {"id": "sales_invoices", "name": "Factures", "desc": "Sales Invoices", "url": "/sales/invoices/", "icon": "sales.png"},
        {"id": "inventory", "name": "Inventari", "desc": "Gestió de Stock", "url": "/inventory/", "icon": "accounting.png"},
        {"id": "analytics", "name": "Analítiques", "desc": "Dashboard i Ràtios", "url": "/analytics/", "icon": "accounting.png"},
        {"id": "users", "name": "Usuaris", "desc": "Gestió d'Usuaris", "url": "/auth/users-page", "icon": "hr.png"},
    ]

    
    for module in module_list:
        if can_access_module(current_user, module["id"]):
            modules.append(module)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": current_user,
        "modules": modules
    })


@app.get("/health")
async def health_check():
    return {"status": "ok"}
