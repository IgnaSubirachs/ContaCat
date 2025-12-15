from sqlalchemy import Column, String, Text
from app.infrastructure.db.base import Base

class CompanySettingsModel(Base):
    __tablename__ = "company_settings"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    tax_id = Column(String(50), nullable=False)
    
    address_street = Column(String(255), nullable=True)
    address_city = Column(String(100), nullable=True)
    address_zip = Column(String(20), nullable=True)
    address_province = Column(String(100), nullable=True)
    address_country = Column(String(100), default="Spain")
    
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    website = Column(String(255), nullable=True)
    
    logo_url = Column(String(500), nullable=True)
    currency = Column(String(3), default="EUR")
