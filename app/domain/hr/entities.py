from dataclasses import dataclass
from datetime import date

@dataclass
class Employee:
    id: str
    first_name: str
    last_name: str
    email: str
    hire_date: date
    is_active: bool = True
