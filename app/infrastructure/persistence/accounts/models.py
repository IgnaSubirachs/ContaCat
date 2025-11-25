from sqlalchemy import String, Integer, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base
from app.domain.accounts.entities import AccountType


class AccountModel(Base):
    """SQLAlchemy model for accounts table."""
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    account_type: Mapped[str] = mapped_column(SQLEnum(AccountType), nullable=False)
    group: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    parent_code: Mapped[str] = mapped_column(String(20), nullable=True)

    def __repr__(self) -> str:
        return f"<AccountModel {self.code} - {self.name}>"
