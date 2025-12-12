from sqlalchemy import Column, String, Boolean
from app.infrastructure.db.base import Base

class BankAccountModel(Base):
    __tablename__ = "bank_accounts"

    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    iban = Column(String(34), nullable=False)
    bic = Column(String(11), nullable=True)
    account_code = Column(String(20), nullable=True)
    currency = Column(String(3), nullable=False, default="EUR")
    is_active = Column(Boolean, nullable=False, default=True)
