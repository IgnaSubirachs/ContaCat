from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class AccountModel(Base):
    __tablename__ = "accounts"

    code: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    account_type: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<AccountModel {self.code} - {self.name}>"
