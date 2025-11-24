from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class PartnerModel(Base):
    """SQLAlchemy model for partners table."""
    __tablename__ = "partners"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    tax_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    is_supplier: Mapped[bool] = mapped_column(Boolean, default=False)
    is_customer: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Fiscal data
    document_type: Mapped[str] = mapped_column(String(20), default="NIF")
    address_street: Mapped[str] = mapped_column(String(200), default="")
    address_number: Mapped[str] = mapped_column(String(20), default="")
    address_floor: Mapped[str] = mapped_column(String(50), default="")
    postal_code: Mapped[str] = mapped_column(String(10), default="")
    city: Mapped[str] = mapped_column(String(100), default="")
    province: Mapped[str] = mapped_column(String(100), default="")
    country: Mapped[str] = mapped_column(String(100), default="España")
    
    # VAT and fiscal regime
    vat_regime: Mapped[str] = mapped_column(String(50), default="GENERAL")
    is_intra_eu: Mapped[bool] = mapped_column(Boolean, default=False)
    eu_vat_number: Mapped[str] = mapped_column(String(30), default="")
    
    # Banking and payment
    iban: Mapped[str] = mapped_column(String(34), default="")
    payment_method: Mapped[str] = mapped_column(String(50), default="TRANSFER")
    payment_days: Mapped[int] = mapped_column(Integer, default=30)

    def __repr__(self) -> str:
        return f"<PartnerModel {self.tax_id} - {self.name}>"
