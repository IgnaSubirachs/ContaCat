from pydantic import BaseModel
from typing import List

class AccountSuggestion(BaseModel):
    account_code: str
    account_name: str
    confidence: float # 0.0 to 1.0
    reason: str
