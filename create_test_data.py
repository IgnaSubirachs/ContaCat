"""
Script to create test data for ERP system.
Creates:
1. Chart of Accounts (essential accounts)
2. Test Customer
"""
import sys
import os
from decimal import Decimal

sys.path.append(os.getcwd())

from app.infrastructure.db.base import SessionLocal
from app.domain.accounts.entities import Account, AccountType
from app.domain.partners.entities import Partner
from app.infrastructure.persistence.accounts.repository import SqlAlchemyAccountRepository
from app.infrastructure.persistence.partners.repository import SqlAlchemyPartnerRepository

def create_test_data():
    print("Creating test data...")
    
    # Use SessionLocal factory
    account_repo = SqlAlchemyAccountRepository(SessionLocal)
    partner_repo = SqlAlchemyPartnerRepository(SessionLocal)
    
    # 1. Create Accounts
    print("1. Creating Accounts...")
    accounts = [
        Account(
            code="430000",
            name="Clients",
            account_type=AccountType.ASSET,
            group=4,
            parent_code="430"
        ),
        Account(
            code="700000",
            name="Vendes de mercaderies",
            account_type=AccountType.INCOME,
            group=7,
            parent_code="700"
        ),
        Account(
            code="477000",
            name="H.P. IVA Repercutit",
            account_type=AccountType.LIABILITY,
            group=4,
            parent_code="477"
        ),
        Account(
            code="572000",
            name="Bancs",
            account_type=AccountType.ASSET,
            group=5,
            parent_code="572"
        )
    ]
    
    for acc in accounts:
        try:
            account_repo.save(acc)
            print(f"   [OK] Account {acc.code} created")
        except Exception as e:
            print(f"   [SKIP] Account {acc.code} already exists or error: {e}")

    # 2. Create Customer
    print("\n2. Creating Customer...")
    customer = Partner(
        name="Empresa de Prova S.L.",
        tax_id="B12345678",
        email="info@prova.com",
        phone="931234567",
        is_customer=True,
        is_supplier=False,
        document_type="NIF",
        address_street="Carrer Major",
        address_number="1",
        city="Barcelona",
        postal_code="08001",
        country="ES"
    )
    
    try:
        partner_repo.add(customer)
        print(f"   [OK] Customer {customer.name} created")
    except Exception as e:
        print(f"   [SKIP] Customer already exists or error: {e}")

    print("\nTest data creation completed!")

if __name__ == "__main__":
    create_test_data()
