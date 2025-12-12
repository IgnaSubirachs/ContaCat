from fastapi import APIRouter, Depends, Query
from typing import List
from sqlalchemy.orm import Session

from app.infrastructure.db.database import get_db
from app.domain.auth.dependencies import get_current_user
from app.domain.auth.entities import User
from app.domain.ai.services import AccountingAssistantService
from app.domain.ai.entities import AccountSuggestion

router = APIRouter(
    prefix="/ai",
    tags=["ai"],
    responses={404: {"description": "Not found"}},
)

def get_ai_service(db: Session = Depends(get_db)) -> AccountingAssistantService:
    return AccountingAssistantService(db)

@router.get("/predict-accounts", response_model=List[AccountSuggestion])
async def predict_accounts(
    description: str = Query(..., min_length=3),
    current_user: User = Depends(get_current_user),
    service: AccountingAssistantService = Depends(get_ai_service)
):
    return service.predict_accounts(description)
