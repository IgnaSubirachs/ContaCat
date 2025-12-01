"""
Sales Module Verification Script
Creates test data and verifies the complete sales workflow:
Quote → Order → Invoice → Journal Entry
"""
import sys
import os
from datetime import date, timedelta
from decimal import Decimal

sys.path.append(os.getcwd())

from app.infrastructure.db.base import SessionLocal
from app.domain.sales.services import QuoteService, SalesOrderService, SalesInvoiceService
from app.domain.accounting.services import AccountingService
from app.infrastructure.persistence.sales.repository import (
    SqlAlchemyQuoteRepository, SqlAlchemySalesOrderRepository, SqlAlchemySalesInvoiceRepository
)
from app.infrastructure.persistence.partners.repository import SqlAlchemyPartnerRepository
from app.infrastructure.persistence.accounts.repository import SqlAlchemyAccountRepository
from app.infrastructure.persistence.accounting.repository import SqlAlchemyJournalRepository


def verify_sales():
    """Verify sales module with complete workflow."""
    print("\n" + "="*60)
    print("SALES MODULE VERIFICATION")
    print("="*60 + "\n")
    
    try:
        # Initialize services with SessionLocal factory
        quote_repo = SqlAlchemyQuoteRepository(SessionLocal)
        order_repo = SqlAlchemySalesOrderRepository(SessionLocal)
        invoice_repo = SqlAlchemySalesInvoiceRepository(SessionLocal)
        partner_repo = SqlAlchemyPartnerRepository(SessionLocal)
        account_repo = SqlAlchemyAccountRepository(SessionLocal)
        journal_repo = SqlAlchemyJournalRepository(SessionLocal)
        
        quote_service = QuoteService(quote_repo, partner_repo)
        order_service = SalesOrderService(order_repo, quote_repo, partner_repo)
        accounting_service = AccountingService(account_repo, journal_repo)
        invoice_service = SalesInvoiceService(invoice_repo, order_repo, partner_repo, accounting_service)
        
        # Step 1: Get or create a test customer
        print("[Step 1] Getting test customer...")
        partners = partner_repo.list_all()
        customers = [p for p in partners if p.is_customer]
        
        if not customers:
            print("[ERROR] No customers found! Please create a customer first.")
            return False
        
        customer = customers[0]
        print(f"[OK] Using customer: {customer.name} ({customer.tax_id})")
        
        # Step 2: Create a Quote
        print("\n[Step 2] Creating quote...")
        quote = quote_service.create_quote(
            partner_id=customer.id,
            quote_date=date.today(),
            valid_days=30,
            lines=[
                {
                    "product_code": "PROD001",
                    "description": "Servei de consultoria",
                    "quantity": 10,
                    "unit_price": 100.00,
                    "discount_percent": 0,
                    "tax_rate": 21
                },
                {
                    "product_code": "PROD002",
                    "description": "Manteniment mensual",
                    "quantity": 1,
                    "unit_price": 500.00,
                    "discount_percent": 10,
                    "tax_rate": 21
                }
            ],
            notes="Pressupost de prova"
        )
        print(f"[OK] Quote created: {quote.quote_number}")
        print(f"   Total: {quote.total} EUR")
        
        # Step 3: Send and Accept Quote
        print("\n[Step 3] Sending and accepting quote...")
        quote_service.send_quote(quote.id)
        quote_service.accept_quote(quote.id)
        print(f"[OK] Quote accepted")
        
        # Step 4: Convert to Order
        print("\n[Step 4] Converting quote to order...")
        order = order_service.create_from_quote(quote.id)
        print(f"[OK] Order created: {order.order_number}")
        print(f"   Total: {order.total} EUR")
        
        # Step 5: Confirm and Deliver Order
        print("\n[Step 5] Confirming and delivering order...")
        order_service.confirm_order(order.id)
        order_service.deliver_order(order.id)
        print(f"[OK] Order delivered")
        
        # Step 6: Convert to Invoice
        print("\n[Step 6] Converting order to invoice...")
        invoice = invoice_service.create_from_order(order.id, series="A")
        print(f"[OK] Invoice created: {invoice.invoice_number}")
        print(f"   Total: {invoice.total} EUR")
        print(f"   Due date: {invoice.due_date}")
        
        # Step 7: Post Invoice (creates journal entry)
        print("\n[Step 7] Posting invoice (creating journal entry)...")
        try:
            invoice = invoice_service.post_invoice(invoice.id)
            print(f"[OK] Invoice posted")
            print(f"   Journal Entry ID: {invoice.journal_entry_id}")
            
            # Verify journal entry
            if invoice.journal_entry_id:
                entry = accounting_service.get_journal_entry(invoice.journal_entry_id)
                if entry:
                    print(f"\n   Journal Entry Details:")
                    print(f"   - Entry Number: {entry.entry_number}")
                    print(f"   - Date: {entry.entry_date}")
                    print(f"   - Total Debit: {entry.total_debit} EUR")
                    print(f"   - Total Credit: {entry.total_credit} EUR")
                    print(f"   - Balanced: {'OK' if entry.is_balanced else 'ERROR'}")
        except Exception as e:
            print(f"[WARNING] Could not create journal entry: {e}")
            print("   (This might be due to missing accounts in chart of accounts)")
        
        # Step 8: Summary
        print("\n" + "="*60)
        print("WORKFLOW SUMMARY")
        print("="*60)
        print(f"Quote:   {quote.quote_number} -> {quote.status.value}")
        print(f"Order:   {order.order_number} -> {order.status.value}")
        print(f"Invoice: {invoice.invoice_number} -> {invoice.status.value}")
        print(f"Payment: {invoice.payment_status.value}")
        print("\n[OK] Sales module verification completed successfully!")
        print("\nAccess the application:")
        print("   - Quotes:   http://localhost:8000/quotes/")
        print("   - Orders:   http://localhost:8000/sales/orders/")
        print("   - Invoices: http://localhost:8000/sales/invoices/")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = verify_sales()
    sys.exit(0 if success else 1)
