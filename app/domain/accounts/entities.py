from dataclasses import dataclass

@dataclass

class Account:
    code: str
    name: str
    account_type: str
    is_active: bool = True