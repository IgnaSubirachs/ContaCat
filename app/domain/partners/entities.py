from dataclasses import dataclass, field
from typing import Optional
import uuid

from app.domain.validators.nif_cif_validator import DocumentValidator
from app.domain.validators.iban_validator import IBANValidator


@dataclass
class Partner:
    """Partner entity representing a customer or supplier."""
    name: str
    tax_id: str  # NIF/CIF/NIE
    email: str
    phone: str
    is_supplier: bool
    is_customer: bool
    
    # Fiscal data
    document_type: str = "NIF"  # NIF, CIF, NIE, PASSPORT, INTRA_EU
    address_street: str = ""
    address_number: str = ""
    address_floor: str = ""
    postal_code: str = ""
    city: str = ""
    province: str = ""
    country: str = "España"
    
    # VAT and fiscal regime
    vat_regime: str = "GENERAL"  # GENERAL, REDUCED, SUPER_REDUCED, EXEMPT, REVERSE_CHARGE, EQUIVALENCE
    is_intra_eu: bool = False
    eu_vat_number: str = ""
    
    # Banking and payment
    iban: str = ""
    payment_method: str = "TRANSFER"  # TRANSFER, CASH, CARD, CHECK, DIRECT_DEBIT
    payment_days: int = 30  # Payment term in days
    
    id: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
    
    def validate(self) -> None:
        """Validate partner data."""
        # Basic validations
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("El nom és obligatori")
        
        if not self.tax_id or len(self.tax_id.strip()) == 0:
            raise ValueError("El NIF/CIF és obligatori")
        
        # Validate document (NIF/CIF/NIE)
        is_valid, doc_type = DocumentValidator.validate_document(self.tax_id)
        if not is_valid and self.document_type not in ["PASSPORT", "INTRA_EU"]:
            raise ValueError(f"El NIF/CIF/NIE '{self.tax_id}' no és vàlid")
        
        # Update document type if detected
        if is_valid and self.document_type in ["NIF", "CIF", "NIE"]:
            self.document_type = doc_type
        
        # Validate IBAN if provided
        if self.iban and self.iban.strip():
            if not IBANValidator.validate_iban(self.iban):
                raise ValueError(f"L'IBAN '{self.iban}' no és vàlid")
        
        # Validate EU VAT number if intra-EU
        if self.is_intra_eu and not self.eu_vat_number:
            raise ValueError("El NIF intracomunitari és obligatori per a operadors intracomunitaris")
        
        # Must be customer, supplier, or both
        if not self.is_customer and not self.is_supplier:
            raise ValueError("El partner ha de ser client, proveïdor o ambdós")
        
        # Validate payment days
        if self.payment_days < 0:
            raise ValueError("Els dies de pagament no poden ser negatius")
    
    @property
    def full_address(self) -> str:
        """Return full formatted address."""
        parts = []
        if self.address_street:
            street = self.address_street
            if self.address_number:
                street += f", {self.address_number}"
            if self.address_floor:
                street += f", {self.address_floor}"
            parts.append(street)
        
        if self.postal_code or self.city:
            city_line = ""
            if self.postal_code:
                city_line = self.postal_code
            if self.city:
                city_line += f" {self.city}" if city_line else self.city
            parts.append(city_line)
        
        if self.province:
            parts.append(self.province)
        
        if self.country and self.country != "España":
            parts.append(self.country)
        
        return ", ".join(parts) if parts else ""
    
    @property
    def formatted_iban(self) -> str:
        """Return formatted IBAN."""
        if not self.iban:
            return ""
        return IBANValidator.format_iban(self.iban)
