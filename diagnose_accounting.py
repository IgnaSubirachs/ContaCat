"""
Diagnostic script to test accounting endpoints.
"""
import sys
sys.path.insert(0, 'c:\\ERP')

print("=" * 60)
print("DIAGNOSTIC D'ENDPOINTS DE COMPTABILITAT")
print("=" * 60)

# Test 1: Import modules
print("\n1. VERIFICANT IMPORTS...")
try:
    from app.domain.accounting.services import AccountingService
    print("  ✓ AccountingService importat correctament")
except Exception as e:
    print(f"  ✗ Error important AccountingService: {e}")
    import traceback
    traceback.print_exc()

try:
    from app.domain.accounting.export_utils import ReportExporter
    print("  ✓ ReportExporter importat correctament")
except Exception as e:
    print(f"  ✗ Error important ReportExporter: {e}")
    import traceback
    traceback.print_exc()

try:
    from app.interface.api.routers import accounting
    print("  ✓ Router accounting importat correctament")
except Exception as e:
    print(f"  ✗ Error important router accounting: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Check templates exist
print("\n2. VERIFICANT PLANTILLES...")
import os

templates = [
    'c:/ERP/app/interface/web/templates/accounting/balance_sheet.html',
    'c:/ERP/app/interface/web/templates/accounting/profit_loss.html',
    'c:/ERP/app/interface/web/templates/accounting/home.html'
]

for template in templates:
    if os.path.exists(template):
        print(f"  ✓ {os.path.basename(template)} existeix")
    else:
        print(f"  ✗ {os.path.basename(template)} NO TROBAT")

# Test 3: Try to instantiate service
print("\n3. VERIFICANT SERVEIS...")
try:
    from app.infrastructure.persistence.accounts.repository import SqlAlchemyAccountRepository
    from app.infrastructure.persistence.accounting.repository import SqlAlchemyJournalRepository
    
    print("  ✓ Repositoris importats correctament")
    
    # Note: This will fail if DB is not running, but that's OK for this test
    try:
        account_repo = SqlAlchemyAccountRepository()
        journal_repo = SqlAlchemyJournalRepository()
        service = AccountingService(account_repo, journal_repo)
        print("  ✓ AccountingService instanciat correctament")
    except Exception as e:
        print(f"  ⚠ No es pot connectar a la BD (normal si no està en marxa): {type(e).__name__}")
        
except Exception as e:
    print(f"  ✗ Error amb els serveis: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Check router endpoints
print("\n4. VERIFICANT ENDPOINTS DEL ROUTER...")
try:
    from app.interface.api.routers.accounting import router
    
    print(f"  Prefix del router: {router.prefix}")
    print(f"  Nombre d'endpoints: {len(router.routes)}")
    
    for route in router.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods = ', '.join(route.methods) if route.methods else 'N/A'
            print(f"    - {methods:6} {route.path}")
            
except Exception as e:
    print(f"  ✗ Error verificant endpoints: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETAT")
print("=" * 60)
