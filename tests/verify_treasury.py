"""
Script de verificació del mòdul de Tresoreria.
Prova la gestió de comptes bancaris i la previsió de tresoreria basada en factures.
"""
import sys
import os
from datetime import date, timedelta
from decimal import Decimal

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.infrastructure.db.base import init_db, SessionLocal
from app.domain.treasury.services import TreasuryService
from app.infrastructure.persistence.treasury.repository import SqlAlchemyTreasuryRepository
from app.infrastructure.persistence.sales.repository import SqlAlchemySalesInvoiceRepository
from app.domain.sales.entities import SalesInvoice, InvoiceStatus

def verify_treasury():
    print("=" * 60)
    print("VERIFICACIÓ MÒDUL DE TRESORERIA")
    print("=" * 60)

    print("\n1. Inicialitzant base de dades...")
    init_db()
    
    session = SessionLocal()
    
    try:
        # Repositories & Services
        treasury_repo = SqlAlchemyTreasuryRepository(session)
        invoice_repo = SqlAlchemySalesInvoiceRepository(session) # To mock/check forecast
        
        # Inject invoice repo into treasury service for forecast
        service = TreasuryService(treasury_repo, invoice_repo)
        
        # 1. Create Bank Account
        print("\n[Step 1] Creant compte bancari...")
        iban_test = "ES9121000000000000001234"
        
        # Cleanup
        accounts = service.list_bank_accounts()
        for acc in accounts:
            if acc.iban == iban_test:
                print(f"   - Compte existent trobat, utilitzant-lo.")
        
        if not any(acc.iban == iban_test for acc in accounts):
            account = service.create_bank_account(
                name="Compte Principal prova",
                iban=iban_test,
                bic="CAIXESBBXXX",
                account_code="5720001"
            )
            print(f"✓ Compte creat: {account.name} ({account.iban})")
        
        # 2. Check Forecast (Previsió de Cobraments)
        print("\n[Step 2] Verificant previsió de tresoreria (Cash Flow)...")
        # We need to ensure there is at least one POSTED invoice.
        # Check existing invoices
        invoices = invoice_repo.list_all()
        posted_invoices = [i for i in invoices if i.status == InvoiceStatus.POSTED]
        
        if not posted_invoices:
            print("   - No hi ha factures comptabilitzades. El forecast d'entrades serà 0.")
        else:
            print(f"   - Trobades {len(posted_invoices)} factures pendents de cobrament.")
            
        forecast = service.get_cash_flow_forecast(days=60)
        
        print(f"✓ Previsió generada per a {forecast['forecast_days']} dies")
        print(f"   - Total Entrades (Inflow): {forecast['total_inflow']} €")
        print(f"   - Total Sortides (Outflow): {forecast['total_outflow']} €")
        print(f"   - Flux Net: {forecast['net_flow']} €")
        
        if forecast['inflow']:
            print("   - Detall Entrades:")
            for item in forecast['inflow'][:5]: # Show max 5
                print(f"     > {item['date']} | {item['amount']}€ | {item['description']}")
        
        print("\n✅ Verificació de Tresoreria completada correctament!")
        return True

    except Exception as e:
        print(f"\n✗ ERROR CRÍTIC: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    success = verify_treasury()
    sys.exit(0 if success else 1)
