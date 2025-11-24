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
        is_customer: bool
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
            is_customer=is_customer
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
