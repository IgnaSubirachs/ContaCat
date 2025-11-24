from typing import List, Optional
from app.domain.partners.entities import Partner
from app.domain.partners.repositories import PartnerRepository


class PartnerService:
    """Service for managing partners (customers and suppliers)."""
    
    def __init__(self, repository: PartnerRepository):
        self._repository = repository
    
    def create_partner(
        self,
        name: str,
        tax_id: str,
        email: str,
        phone: str,
        is_supplier: bool,
        is_customer: bool,
        # Fiscal data (optional with defaults)
        document_type: str = "NIF",
        address_street: str = "",
        address_number: str = "",
        address_floor: str = "",
        postal_code: str = "",
        city: str = "",
        province: str = "",
        country: str = "España",
        vat_regime: str = "GENERAL",
        is_intra_eu: bool = False,
        eu_vat_number: str = "",
        iban: str = "",
        payment_method: str = "TRANSFER",
        payment_days: int = 30,
    ) -> Partner:
        """Create a new partner."""
        # Check if tax_id already exists
        existing = self._repository.find_by_tax_id(tax_id)
        if existing:
            raise ValueError(f"Ja existeix un partner amb el NIF/CIF {tax_id}")
        
        # Create and validate partner
        partner = Partner(
            name=name,
            tax_id=tax_id,
            email=email,
            phone=phone,
            is_supplier=is_supplier,
            is_customer=is_customer,
            document_type=document_type,
            address_street=address_street,
            address_number=address_number,
            address_floor=address_floor,
            postal_code=postal_code,
            city=city,
            province=province,
            country=country,
            vat_regime=vat_regime,
            is_intra_eu=is_intra_eu,
            eu_vat_number=eu_vat_number,
            iban=iban,
            payment_method=payment_method,
            payment_days=payment_days,
        )
        partner.validate()
        
        # Save to repository
        self._repository.add(partner)
        return partner
    
    def list_all_partners(self) -> List[Partner]:
        """List all partners."""
        return self._repository.list_all()
    
    def get_partner_by_id(self, partner_id: str) -> Optional[Partner]:
        """Get a partner by ID."""
        return self._repository.find_by_id(partner_id)
    
    def get_customers(self) -> List[Partner]:
        """Get all customers."""
        all_partners = self._repository.list_all()
        return [p for p in all_partners if p.is_customer]
    
    def get_suppliers(self) -> List[Partner]:
        """Get all suppliers."""
        all_partners = self._repository.list_all()
        return [p for p in all_partners if p.is_supplier]
    
    def update_partner(
        self,
        partner_id: str,
        name: str,
        email: str,
        phone: str,
        is_supplier: bool,
        is_customer: bool,
        # Fiscal data
        address_street: str = "",
        address_number: str = "",
        address_floor: str = "",
        postal_code: str = "",
        city: str = "",
        province: str = "",
        country: str = "España",
        vat_regime: str = "GENERAL",
        is_intra_eu: bool = False,
        eu_vat_number: str = "",
        iban: str = "",
        payment_method: str = "TRANSFER",
        payment_days: int = 30,
    ) -> Partner:
        """Update an existing partner."""
        partner = self._repository.find_by_id(partner_id)
        if not partner:
            raise ValueError(f"No s'ha trobat el partner amb ID {partner_id}")
        
        # Update fields
        partner.name = name
        partner.email = email
        partner.phone = phone
        partner.is_supplier = is_supplier
        partner.is_customer = is_customer
        partner.address_street = address_street
        partner.address_number = address_number
        partner.address_floor = address_floor
        partner.postal_code = postal_code
        partner.city = city
        partner.province = province
        partner.country = country
        partner.vat_regime = vat_regime
        partner.is_intra_eu = is_intra_eu
        partner.eu_vat_number = eu_vat_number
        partner.iban = iban
        partner.payment_method = payment_method
        partner.payment_days = payment_days
        
        partner.validate()
        self._repository.update(partner)
        return partner
    
    def delete_partner(self, partner_id: str) -> None:
        """Delete a partner."""
        partner = self._repository.find_by_id(partner_id)
        if not partner:
            raise ValueError(f"No s'ha trobat el partner amb ID {partner_id}")
        
        self._repository.delete(partner_id)
