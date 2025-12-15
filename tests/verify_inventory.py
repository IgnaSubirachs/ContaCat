import sys
import os
from datetime import date
from decimal import Decimal

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.infrastructure.db.base import SessionLocal, init_db
from app.infrastructure.persistence.inventory.repositories import SqlAlchemyStockItemRepository, SqlAlchemyStockMovementRepository
from app.infrastructure.persistence.sales.repository import SqlAlchemySalesInvoiceRepository, SqlAlchemySalesOrderRepository
from app.infrastructure.persistence.partners.repository import SqlAlchemyPartnerRepository
from app.infrastructure.persistence.accounts.repository import SqlAlchemyAccountRepository
from app.infrastructure.persistence.accounting.repository import SqlAlchemyJournalRepository
from app.infrastructure.persistence.audit.repository import SqlAlchemyAuditRepository

from app.domain.inventory.services import InventoryService
from app.domain.inventory.entities import StockItem
from app.domain.sales.services import SalesInvoiceService
from app.domain.accounting.services import AccountingService
from app.domain.accounting.mapping_service import AccountMappingService
from app.domain.audit.services import AuditService

def run_verification():
    print("[INFO] Iniciant Injeccio de Dependencies per Test d'Inventari...")
    
    # 1. Repositories
    db_session = SessionLocal
    stock_repo = SqlAlchemyStockItemRepository(db_session)
    movement_repo = SqlAlchemyStockMovementRepository(db_session)
    invoice_repo = SqlAlchemySalesInvoiceRepository(db_session)
    order_repo = SqlAlchemySalesOrderRepository(db_session)
    partner_repo = SqlAlchemyPartnerRepository(db_session)
    account_repo = SqlAlchemyAccountRepository(db_session)
    journal_repo = SqlAlchemyJournalRepository(db_session)
    audit_repo = SqlAlchemyAuditRepository(db_session)

    # 2. Services
    inventory_service = InventoryService(stock_repo, movement_repo)
    accounting_service = AccountingService(account_repo, journal_repo)
    mapping_service = AccountMappingService()
    audit_service = AuditService(audit_repo)
    
    # 3. Sales Service (The Target)
    sales_service = SalesInvoiceService(
        invoice_repo, order_repo, partner_repo, accounting_service, 
        mapping_service, audit_service, inventory_service
    )

    print("[OK] Serveis inicialitzats.")

    # 4. Scenario Setup
    stock_code = "ITEM-TEST-INV-001"
    
    # Check if item exists, if not create
    item = stock_repo.find_by_code(stock_code)
    if not item:
        print(f"[INFO] Creant article de prova: {stock_code}")
        item = StockItem(
            code=stock_code,
            name="Article Test Inventari",
            unit_price=50.0,
            quantity=100  # Initial Stock
        )
        stock_repo.save(item)
    else:
        # Reset stock to 100 for consistent test
        item.quantity = 100
        stock_repo.save(item)
    
    print(f"[INFO] Stock Inicial: {item.quantity}")

    # 5. Create Invoice
    print("[INFO] Creant Factura de Venda...")
    invoice_lines = [
        {
            "product_code": stock_code,
            "description": "Venda Test Stock",
            "quantity": 5,
            "unit_price": 50.0,
            "tax_rate": 21
        }
    ]

    # Get a legitimate partner (assuming ID 1 exists from previous tests or verify_sales)
    # If not, let's create a dummy or fetch first
    partners = partner_repo.list_all()
    if not partners:
        print("[ERROR] No partners found. Run verify_sales.py setup first if needed.")
        return
    
    partner_id = partners[0].id
    
    invoice = sales_service.create_invoice(
        partner_id=partner_id,
        invoice_date=date.today(),
        lines=invoice_lines
    )
    print(f"[INFO] Factura Creada: {invoice.invoice_number}")

    # 6. Post Invoice (Trigger Stock Move)
    print("[INFO] Comptabilitzant Factura (Trigger Stock)...")
    sales_service.post_invoice(invoice.id, user="TEST_SCRIPT")

    # 7. Verification
    print("[INFO] Verificant Resultats...")
    
    # 7a. Check Stock Level
    updated_item = stock_repo.find_by_code(stock_code)
    print(f"[INFO] Stock Final: {updated_item.quantity}")
    
    if updated_item.quantity == 95:
        print("[SUCCESS] Stock reduit correctament (100 - 5 = 95).")
    else:
        print(f"[FAILURE] Stock esperat 95, trobat {updated_item.quantity}.")

    # 7b. Check Movement Log
    movements = inventory_service.list_movements(stock_code)
    last_move = movements[0] if movements else None
    
    if last_move and last_move.quantity == -5:
         print(f"[SUCCESS] Moviment registrat correctament ({last_move.quantity}).")
    else:
         print(f"[FAILURE] No s'ha trobat el moviment adequat.")

if __name__ == "__main__":
    try:
        run_verification()
    except Exception as e:
        print(f"[ERROR] EXCEPCIO: {e}")
        import traceback
        traceback.print_exc()
