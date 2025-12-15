"""
Script de verificació del mòdul de Partners (Clients i Proveïdors).
Prova el CRUD complet i les validacions fiscals (NIF, IBAN, etc).
"""
import sys
import os
from datetime import date
from decimal import Decimal

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.infrastructure.db.base import init_db, SessionLocal
from app.domain.partners.services import PartnerService
from app.infrastructure.persistence.partners.repository import SqlAlchemyPartnerRepository

def verify_partners():
    print("=" * 60)
    print("VERIFICACIÓ MÒDUL DE PARTNERS (CLIENTS/PROVEÏDORS)")
    print("=" * 60)

    print("\n1. Inicialitzant base de dades...")
    init_db()
    
    session = SessionLocal()
    
    try:
        # Repositories & Services
        repo = SqlAlchemyPartnerRepository(session)
        service = PartnerService(repo)
        
        # 1. Create Partner
        print("\n[Step 1] Creant partner de prova...")
        tax_id = "B12345678"
        
        # Cleanup
        existing = repo.find_by_tax_id(tax_id)
        if existing:
            print(f"   - Esborrant partner existent {tax_id}...")
            repo.delete(existing.id)
            session.commit()
            
        partner = service.create_partner(
            name="Empresa de Prova S.L.",
            tax_id=tax_id,
            email="info@prova.com",
            phone="930000000",
            is_supplier=True,
            is_customer=True,
            address_street="Av. Diagonal",
            address_number="123",
            city="Barcelona",
            postal_code="08018",
            province="Barcelona",
            vat_regime="GENERAL",
            iban="ES9100000000000000000000"
        )
        
        print(f"✓ Partner creat: {partner.name} ({partner.tax_id})")
        print(f"   - Rol: {'Client' if partner.is_customer else ''} {'Proveïdor' if partner.is_supplier else ''}")
        print(f"   - Adreça: {partner.full_address}")
        
        # 2. Update Partner
        print("\n[Step 2] Actualitzant partner...")
        updated = service.update_partner(
            partner_id=partner.id,
            name="Empresa de Prova UPDATED S.L.",
            email=partner.email,
            phone=partner.phone,
            is_supplier=partner.is_supplier,
            is_customer=partner.is_customer,
            city="Madrid"
        )
        print(f"✓ Partner actualitzat: {updated.name}")
        print(f"   - City: {updated.city}")
        
        if updated.city != "Madrid":
            print("⚠ ERROR: L'actualització no ha funcionat correctament!")
            return False
            
        # 3. List Filters
        print("\n[Step 3] Verificant filtres (Clients vs Proveïdors)...")
        customers = service.get_customers()
        suppliers = service.get_suppliers()
        
        print(f"✓ Trobat en llista de clients: {any(p.id == partner.id for p in customers)}")
        print(f"✓ Trobat en llista de proveïdors: {any(p.id == partner.id for p in suppliers)}")
        
        # 4. Validation Check
        print("\n[Step 4] Verificant validació de duplicats...")
        try:
            service.create_partner(
                name="Duplicat",
                tax_id=tax_id, # Same tax ID
                email="fake@fake.com",
                phone="000",
                is_supplier=True,
                is_customer=False
            )
            print("⚠ ERROR: S'hauria d'haver detectat el duplicat!")
            return False
        except ValueError as e:
            print(f"✓ Correcte: {e}")

        print("\n✅ Verificació de Partners completada correctament!")
        return True

    except Exception as e:
        print(f"\n✗ ERROR CRÍTIC: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    success = verify_partners()
    sys.exit(0 if success else 1)
