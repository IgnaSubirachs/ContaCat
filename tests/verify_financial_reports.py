"""
Script to verify financial reports functionality.
Tests Balance Sheet and Profit & Loss reports.
"""
import sys
from datetime import date, timedelta
from decimal import Decimal

# Add project root to path
sys.path.insert(0, 'c:\\ERP')

from app.domain.accounting.services import AccountingService
from app.domain.accounts.entities import AccountType
from app.infrastructure.persistence.accounts.repository import SqlAlchemyAccountRepository
from app.infrastructure.persistence.accounting.repository import SqlAlchemyJournalRepository


def test_financial_reports():
    """Test financial reports generation."""
    print("=" * 60)
    print("VERIFICACIÓ D'INFORMES FINANCERS")
    print("=" * 60)
    
    # Initialize services
    account_repo = SqlAlchemyAccountRepository()
    journal_repo = SqlAlchemyJournalRepository()
    accounting_service = AccountingService(account_repo, journal_repo)
    
    # Test 1: Balance Sheet
    print("\n1. BALANÇ DE SITUACIÓ")
    print("-" * 60)
    try:
        balance_sheet = accounting_service.get_balance_sheet()
        
        print(f"✓ Balanç generat correctament")
        print(f"  - Total Actiu: {balance_sheet['total_actiu']} €")
        print(f"  - Total Passiu: {balance_sheet['total_passiu']} €")
        print(f"  - Total Patrimoni Net: {balance_sheet['total_patrimoni_net']} €")
        
        # Check balance
        equilibri = balance_sheet['total_actiu'] - balance_sheet['total_passiu'] - balance_sheet['total_patrimoni_net']
        if equilibri == 0:
            print(f"  ✓ El balanç quadra (equilibri = 0)")
        else:
            print(f"  ⚠ ADVERTÈNCIA: El balanç no quadra (equilibri = {equilibri})")
        
        # Show account counts
        actiu_nc_count = len(balance_sheet['actiu']['no_corrent'])
        actiu_c_count = len(balance_sheet['actiu']['corrent'])
        passiu_nc_count = len(balance_sheet['passiu']['no_corrent'])
        passiu_c_count = len(balance_sheet['passiu']['corrent'])
        pn_count = len(balance_sheet['patrimoni_net'])
        
        print(f"\n  Comptes per categoria:")
        print(f"  - Actiu No Corrent: {actiu_nc_count}")
        print(f"  - Actiu Corrent: {actiu_c_count}")
        print(f"  - Passiu No Corrent: {passiu_nc_count}")
        print(f"  - Passiu Corrent: {passiu_c_count}")
        print(f"  - Patrimoni Net: {pn_count}")
        
    except Exception as e:
        print(f"✗ Error generant el Balanç de Situació: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Profit & Loss
    print("\n2. COMPTE DE PÈRDUES I GUANYS")
    print("-" * 60)
    try:
        # Test with different periods
        today = date.today()
        start_of_year = date(today.year, 1, 1)
        
        # All time
        profit_loss_all = accounting_service.get_profit_loss()
        print(f"✓ PyG (tot el període) generat correctament")
        print(f"  - Total Ingressos: {profit_loss_all['total_ingressos']} €")
        print(f"  - Total Despeses: {profit_loss_all['total_despeses']} €")
        print(f"  - Resultat: {profit_loss_all['resultat']} €")
        
        if profit_loss_all['resultat'] >= 0:
            print(f"  ✓ Resultat POSITIU (Benefici)")
        else:
            print(f"  ⚠ Resultat NEGATIU (Pèrdua)")
        
        # Year to date
        profit_loss_ytd = accounting_service.get_profit_loss(start_of_year, today)
        print(f"\n✓ PyG (any {today.year}) generat correctament")
        print(f"  - Total Ingressos: {profit_loss_ytd['total_ingressos']} €")
        print(f"  - Total Despeses: {profit_loss_ytd['total_despeses']} €")
        print(f"  - Resultat: {profit_loss_ytd['resultat']} €")
        
        # Show account counts
        income_count = len(profit_loss_all['ingressos'])
        expense_count = len(profit_loss_all['despeses'])
        
        print(f"\n  Comptes per categoria (tot el període):")
        print(f"  - Ingressos: {income_count}")
        print(f"  - Despeses: {expense_count}")
        
    except Exception as e:
        print(f"✗ Error generant el Compte de PyG: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Export functionality
    print("\n3. FUNCIONALITAT D'EXPORTACIÓ")
    print("-" * 60)
    try:
        from app.domain.accounting.export_utils import ReportExporter
        import tempfile
        import os
        
        # Test PDF export for Balance Sheet
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            ReportExporter.export_balance_sheet_to_pdf(balance_sheet, temp_pdf.name)
            pdf_size = os.path.getsize(temp_pdf.name)
            print(f"✓ Balanç exportat a PDF ({pdf_size} bytes)")
            os.unlink(temp_pdf.name)
        
        # Test Excel export for Balance Sheet
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_excel:
            ReportExporter.export_balance_sheet_to_excel(balance_sheet, temp_excel.name)
            excel_size = os.path.getsize(temp_excel.name)
            print(f"✓ Balanç exportat a Excel ({excel_size} bytes)")
            os.unlink(temp_excel.name)
        
        # Test PDF export for P&L
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            ReportExporter.export_profit_loss_to_pdf(profit_loss_all, temp_pdf.name)
            pdf_size = os.path.getsize(temp_pdf.name)
            print(f"✓ PyG exportat a PDF ({pdf_size} bytes)")
            os.unlink(temp_pdf.name)
        
        # Test Excel export for P&L
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_excel:
            ReportExporter.export_profit_loss_to_excel(profit_loss_all, temp_excel.name)
            excel_size = os.path.getsize(temp_excel.name)
            print(f"✓ PyG exportat a Excel ({excel_size} bytes)")
            os.unlink(temp_excel.name)
        
    except Exception as e:
        print(f"✗ Error en l'exportació: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Summary
    print("\n" + "=" * 60)
    print("RESUM DE LA VERIFICACIÓ")
    print("=" * 60)
    print("✓ Balanç de Situació: OK")
    print("✓ Compte de Pèrdues i Guanys: OK")
    print("✓ Exportació PDF/Excel: OK")
    print("\n✅ TOTS ELS TESTS HAN PASSAT CORRECTAMENT!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    try:
        success = test_financial_reports()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ ERROR CRÍTIC: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
