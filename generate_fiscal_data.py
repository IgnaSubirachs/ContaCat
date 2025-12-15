import sys
import os
from datetime import date
from decimal import Decimal

sys.path.insert(0, os.getcwd())

from app.infrastructure.db.base import SessionLocal
from app.domain.accounting.entities import JournalEntry, JournalLine, JournalEntryStatus
from app.infrastructure.persistence.accounting.repository import SqlAlchemyJournalRepository

def create_entry(repo, date_obj, desc, lines):
    entry_number = repo.get_next_entry_number()
    entry = JournalEntry(
        entry_number=entry_number,
        entry_date=date_obj,
        description=desc,
        status=JournalEntryStatus.POSTED,
        lines=lines
    )
    repo.add(entry)
    print(f"Created entry {entry_number}: {desc}")

def generate_data():
    repo = SqlAlchemyJournalRepository(SessionLocal)
    
    # OUTPUT VAT (Sales) - 4T 2025 (Dec)
    # Sale 1: Base 1000, VAT 21%
    create_entry(repo, date(2025, 12, 5), "Venda Test 1", [
        JournalLine(account_code="43000000", debit=Decimal("1210"), credit=Decimal("0"), description="Client"),
        JournalLine(account_code="70000000", debit=Decimal("0"), credit=Decimal("1000"), description="Venda"),
        JournalLine(account_code="47700000", debit=Decimal("0"), credit=Decimal("210"), description="IVA 21% factura TEST1")
    ])
    
    # Sale 2: Base 500, VAT 10%
    create_entry(repo, date(2025, 12, 10), "Venda Test 2", [
        JournalLine(account_code="43000000", debit=Decimal("550"), credit=Decimal("0"), description="Client"),
        JournalLine(account_code="70000000", debit=Decimal("0"), credit=Decimal("500"), description="Venda"),
        JournalLine(account_code="47700000", debit=Decimal("0"), credit=Decimal("50"), description="IVA 10% factura TEST2")
    ])

    # INPUT VAT (Purchases) - 4T 2025
    # Purchase 1: Base 200, VAT 21%
    create_entry(repo, date(2025, 12, 1), "Compra Test 1", [
        JournalLine(account_code="60000000", debit=Decimal("200"), credit=Decimal("0"), description="Despesa"),
        JournalLine(account_code="47200000", debit=Decimal("42"), credit=Decimal("0"), description="IVA 21% compra TEST3"),
        JournalLine(account_code="40000000", debit=Decimal("0"), credit=Decimal("242"), description="Proveidor")
    ])
    
    # Previous Month (Nov)
    create_entry(repo, date(2025, 11, 20), "Venda Nov", [
        JournalLine(account_code="43000000", debit=Decimal("2420"), credit=Decimal("0"), description="Client"),
        JournalLine(account_code="70000000", debit=Decimal("0"), credit=Decimal("2000"), description="Venda"),
        JournalLine(account_code="47700000", debit=Decimal("0"), credit=Decimal("420"), description="IVA 21% factura NOV")
    ])
    
    print("Data generation complete.")

if __name__ == "__main__":
    generate_data()
