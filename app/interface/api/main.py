from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional
import os

from app.interface.api.routers import partners, accounting, accounts, quotes, sales_orders, sales_invoices, auth, assets, inventory, fiscal, analytics, treasury, budgets, finance, banking, ai, hr
from app.domain.auth.dependencies import get_current_user_or_redirect, can_access_module
from app.domain.auth.entities import User
from app.interface.api.templates import templates

# Initialize App
app = FastAPI(title="ContaCAT", description="ERP Modular amb DDD", version="2.0.0")

# Determine paths relative to this file
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
static_dir = os.path.join(project_root, "frontend/static")

# Mount static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include routers
app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(accounting.router)
app.include_router(sales_invoices.router)
app.include_router(sales_orders.router)
app.include_router(quotes.router)
app.include_router(partners.router)
app.include_router(hr.router) # Unified HR Router
app.include_router(assets.router)
app.include_router(analytics.router)
app.include_router(fiscal.router)
app.include_router(inventory.router)
app.include_router(treasury.router)
app.include_router(budgets.router)
app.include_router(finance.router)
app.include_router(banking.router)
app.include_router(ai.router)
from app.interface.api.routers import settings
app.include_router(settings.router)


@app.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_or_redirect)
):
    """Home page with navigation to all modules (requires login)."""
    if current_user is None:
        return RedirectResponse(url="/auth/login-page", status_code=302)
    
    # Build list of accessible modules grouped by category
    grouped_modules = {}
    
    # Define all modules with categories and icons
    all_modules = [
        # Sales & Partners
        {"id": "partners", "name": "Clients i Prov.", "desc": "Gestió de contactes", "url": "/partners/", "icon": "fa-users", "category": "Vendes i Relacions"},
        {"id": "quotes", "name": "Pressupostos", "desc": "Ofertes comercials", "url": "/quotes/", "icon": "fa-file-contract", "category": "Vendes i Relacions"},
        {"id": "sales_orders", "name": "Comandes", "desc": "Comandes de clients", "url": "/sales/orders/", "icon": "fa-shopping-cart", "category": "Vendes i Relacions"},
        {"id": "sales_invoices", "name": "Factures", "desc": "Facturació a clients", "url": "/sales/invoices/", "icon": "fa-file-invoice-dollar", "category": "Vendes i Relacions"},
        
        # Finance & Accounting
        {"id": "accounting", "name": "Comptabilitat", "desc": "Diari i Assentaments", "url": "/accounting/", "icon": "fa-book", "category": "Finances i Comptabilitat"},
        {"id": "accounts", "name": "Pla Comptable", "desc": "Gestió de comptes", "url": "/accounts/", "icon": "fa-list-ol", "category": "Finances i Comptabilitat"},
        {"id": "treasury", "name": "Tresoreria", "desc": "Bancs i Caixa", "url": "/treasury/", "icon": "fa-university", "category": "Finances i Comptabilitat"},
        {"id": "fiscal", "name": "Fiscalitat", "desc": "Impostos i models", "url": "/fiscal/", "icon": "fa-landmark", "category": "Finances i Comptabilitat"},
        {"id": "budgets", "name": "Pressupostos", "desc": "Control pressupostari", "url": "/budgets/", "icon": "fa-chart-pie", "category": "Finances i Comptabilitat"},
        {"id": "assets", "name": "Actius Fixos", "desc": "Amortitzacions", "url": "/assets/", "icon": "fa-building", "category": "Finances i Comptabilitat"},
        
        # HR
        {"id": "employees", "name": "Empleats", "desc": "Fitxa de treballadors", "url": "/hr/employees", "icon": "fa-user-tie", "category": "Recursos Humans"},
        {"id": "payrolls", "name": "Nòmines", "desc": "Gestió salarial", "url": "/hr/payroll", "icon": "fa-file-alt", "category": "Recursos Humans"},
        
        # Operations & Analytics
        {"id": "inventory", "name": "Inventari", "desc": "Stock i Productes", "url": "/inventory/", "icon": "fa-boxes", "category": "Operacions"},
        {"id": "analytics", "name": "Analítica", "desc": "Informes i KPIs", "url": "/analytics/", "icon": "fa-chart-line", "category": "Operacions"},
        
        # Admin
        {"id": "users", "name": "Usuaris", "desc": "Accés al sistema", "url": "/auth/users-page", "icon": "fa-user-shield", "category": "Administració"},
    ]
    
    # Filter by permission and group
    for module in all_modules:
        if can_access_module(current_user, module["id"]):
            cat = module["category"]
            if cat not in grouped_modules:
                grouped_modules[cat] = []
            grouped_modules[cat].append(module)
            
    # Dashboard Data
    from app.domain.analytics.dashboard_service import DashboardService
    from app.infrastructure.db.base import SessionLocal
    
    dashboard_service = DashboardService(SessionLocal)
    kpis = dashboard_service.get_kpis()
    trend = dashboard_service.get_sales_trend()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": current_user,
        "grouped_modules": grouped_modules,
        "kpis": kpis,
        "trend_labels": trend["labels"],
        "trend_data": trend["data"]
    })


@app.get("/health")
async def health_check():
    return {"status": "ok"}
