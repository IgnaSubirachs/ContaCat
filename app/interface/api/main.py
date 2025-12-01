from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os

from app.interface.api.routers import partners
from app.interface.api.routers import employees
from app.interface.api.routers import accounting
from app.interface.api.routers import accounts
from app.interface.api.routers import quotes
from app.interface.api.routers import sales_orders
from app.interface.api.routers import sales_invoices
from app.interface.api.routers import auth

app = FastAPI(title="ContaCAT", description="ERP Modular amb DDD", version="2.0.0")

# Determine paths relative to this file
current_dir = os.path.dirname(os.path.abspath(__file__))
web_dir = os.path.join(current_dir, "../web")
static_dir = os.path.join(web_dir, "static")
templates_dir = os.path.join(web_dir, "templates")

# Mount static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Templates
templates = Jinja2Templates(directory=templates_dir)

# Include routers
app.include_router(auth.router)
app.include_router(partners.router)
app.include_router(employees.router)
app.include_router(accounts.router)
app.include_router(accounting.router)
app.include_router(quotes.router)
app.include_router(sales_orders.router)
app.include_router(sales_invoices.router)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "ok"}
