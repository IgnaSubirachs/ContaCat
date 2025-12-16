from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import List, Optional
from sqlalchemy.orm import Session

from app.infrastructure.db.database import get_db
from app.domain.auth.dependencies import get_current_user, get_current_user_or_redirect
from app.domain.auth.entities import User
from app.domain.ai.services import AccountingAssistantService
from app.domain.ai.entities import AccountSuggestion
from app.interface.api.templates import templates

router = APIRouter(
    prefix="/ai",
    tags=["ai"],
    responses={404: {"description": "Not found"}},
)

def get_ai_service(db: Session = Depends(get_db)) -> AccountingAssistantService:
    return AccountingAssistantService(db)

@router.get("/", response_class=HTMLResponse)
async def ai_chat_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_or_redirect)
):
    """Render AI chat interface."""
    if current_user is None:
        return RedirectResponse(url="/auth/login-page", status_code=302)
    
    return templates.TemplateResponse("ai/chat.html", {
        "request": request,
        "user": current_user
    })

@router.get("/predict-accounts", response_model=List[AccountSuggestion])
async def predict_accounts(
    description: str = Query(..., min_length=3),
    current_user: User = Depends(get_current_user),
    service: AccountingAssistantService = Depends(get_ai_service)
):
    return service.predict_accounts(description)
