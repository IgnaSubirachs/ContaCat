from dataclasses import dataclass, field
from typing import Optional
import uuid

@dataclass
class CompanySettings:
    """Settings regarding the company itself."""
    name: str
    tax_id: str  # NIF/CIF
    
    # Address
    address_street: str = ""
    address_city: str = ""
    address_zip: str = ""
    address_province: str = ""
    address_country: str = "Spain"
    
    # Contact
    email: str = ""
    phone: str = ""
    website: str = ""
    
    # Branding
    logo_url: Optional[str] = None
    
    # Fiscal
    currency: str = "EUR"
    
    # Email/SMTP Configuration
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_from_name: str = ""
    smtp_use_tls: bool = True
    
    # SII (AEAT) Configuration
    sii_enabled: bool = False
    sii_test_mode: bool = True
    sii_certificate_path: str = ""
    sii_certificate_password: str = ""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    @property
    def full_address(self) -> str:
        """Return formatted address."""
        parts = [self.address_street, self.address_zip + " " + self.address_city, self.address_province]
        return ", ".join([p for p in parts if p])
