from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os

from app.interface.api.routers import partners

app = FastAPI(title="ERP Català", description="ERP Modular amb DDD", version="1.0.0")

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
app.include_router(partners.router)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "ok"}
