from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import json

from app.domain.analytics.services import AnalyticsService
from app.domain.auth.dependencies import get_current_active_user, require_role
from app.domain.auth.entities import User, UserRole
from app.infrastructure.db.base import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/analytics", tags=["analytics"])
templates = Jinja2Templates(directory="app/interface/web/templates")


def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db)


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    fiscal_year_id: Optional[int] = None,
    service: AnalyticsService = Depends(get_analytics_service),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER, UserRole.READ_ONLY))
):
    """Financial analytics dashboard."""
    summary = service.get_summary_data(fiscal_year_id)
    ratios = service.calculate_ratios(fiscal_year_id)
    chart_data = service.get_chart_data(fiscal_year_id)
    
    return templates.TemplateResponse("analytics/dashboard.html", {
        "request": request,
        "user": current_user,
        "summary": summary,
        "ratios": ratios,
        "chart_data": json.dumps(chart_data),
    })


@router.get("/api/ratios")
async def get_ratios(
    fiscal_year_id: Optional[int] = None,
    service: AnalyticsService = Depends(get_analytics_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get financial ratios as JSON."""
    ratios = service.calculate_ratios(fiscal_year_id)
    return {
        "current_ratio": float(ratios.current_ratio) if ratios.current_ratio else None,
        "solvency_ratio": float(ratios.solvency_ratio) if ratios.solvency_ratio else None,
        "debt_ratio": float(ratios.debt_ratio) if ratios.debt_ratio else None,
        "roa": float(ratios.roa) if ratios.roa else None,
        "roe": float(ratios.roe) if ratios.roe else None,
    }
