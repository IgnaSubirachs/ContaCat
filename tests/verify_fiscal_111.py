import sys
import os
from datetime import date
from decimal import Decimal

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.db.base import SessionLocal
from app.infrastructure.persistence.hr.repository import SqlAlchemyEmployeeRepository, SqlAlchemyPayrollRepository
from app.infrastructure.persistence.accounting.repository import SqlAlchemyJournalRepository
from app.infrastructure.persistence.settings.repository import SqlAlchemyCompanySettingsRepository
from app.domain.hr.services import EmployeeService, PayrollService
from app.domain.fiscal.services import FiscalModelService
from app.domain.settings.services import SettingsService
from app.domain.accounting.entities import JournalEntry, JournalLine, JournalEntryStatus

def verify_model_111():
    print("Verifying Model 111 Calculation...")
    # db = SessionLocal() # Not needed if repos take factory
    try:
        # Repositories expects Session Factory
        emp_repo = SqlAlchemyEmployeeRepository(SessionLocal)
        pay_repo = SqlAlchemyPayrollRepository(SessionLocal)
        journal_repo = SqlAlchemyJournalRepository(SessionLocal)
        settings_repo = SqlAlchemyCompanySettingsRepository(SessionLocal)
        
        # Services
        emp_service = EmployeeService(emp_repo)
        pay_service = PayrollService(pay_repo, emp_repo)
        settings_service = SettingsService(settings_repo)
        fiscal_service = FiscalModelService(journal_repo, settings_service, pay_repo)
        
        # 1. Setup Test Data (Employee + Payroll) for Q4 2025
        print("1. Creating Employee & Payroll...")
        try:
             emp = emp_service.create_employee("Test", "Fiscal", "99999999R", "t@t.com", "123", "Dev", "IT", date(2025, 10, 1), Decimal("3000"))
        except ValueError:
             emp = emp_repo.find_by_dni("99999999R")
        
        # Ensure retention
        emp.irpf_retention = Decimal("10.00")
        emp_repo.update(emp)
        
        # Generate Payroll Oct 2025
        # 3000 * 10% = 300 IRPF
        pay_oct = pay_service.calculate_payroll(emp.id, 10, 2025)
        # Set to PAID to be included in Model 111
        from app.domain.hr.entities import PayrollStatus
        pay_oct.status = PayrollStatus.PAID
        pay_repo.update(pay_oct)
        
        print(f"   Payroll Generated: Gross {pay_oct.gross_salary}, IRPF {pay_oct.irpf_amount}, Status {pay_oct.status}")
        
        # 2a. Ensure Accounts exist
        from app.domain.accounts.entities import Account, AccountType
        from app.infrastructure.persistence.accounts.repository import SqlAlchemyAccountRepository
        acc_repo = SqlAlchemyAccountRepository(SessionLocal)
        
        for code, name in [("62300000", "Serveis Professionals"), ("47510000", "HP Creditora IRPF"), ("41000000", "Creditors")]:
             if not acc_repo.find_by_code(code):
                 acc_repo.add(Account(
                     code=code, 
                     name=name, 
                     account_type=AccountType.LIABILITY if code.startswith("4") else AccountType.EXPENSE,
                     # description="Test Account", # Removed
                     group=code[0], # Added group
                     parent_code=code[:3]
                 ))

        # 2b. Creating Professional Invoice Journal Entry...
        # Credit 4751 (Liability) = 150 (We owe 150 to Hacienda)
        # Debit 623 (Professional Services) = 1000
        # Credit 410 (Creditor) = 850
        import random
        entry = JournalEntry(
            entry_number=random.randint(100000, 999999), # Avoid duplicate
            entry_date=date(2025, 11, 15),
            description="Factura Notari (Retencion 15%)",
            status=JournalEntryStatus.POSTED,
            lines=[
                JournalLine(account_code="62300000", debit=Decimal("1000"), credit=Decimal("0"), description="Serveis Professionals"),
                JournalLine(account_code="47510000", debit=Decimal("0"), credit=Decimal("150"), description="IRPF 15% Notari"),
                JournalLine(account_code="41000000", debit=Decimal("0"), credit=Decimal("850"), description="Notari Obligacion")
            ]
        )
        journal_repo.add(entry)
        print("   Journal Entry created (150 IRPF)")
        
        # 3. Calculate Model 111 4T 2025
        print("3. Calculating Model 111 (4T 2025)...")
        start_date = date(2025, 10, 1)
        end_date = date(2025, 12, 31)
        
        model = fiscal_service.calculate_model_111(2025, "4T", start_date, end_date)
        
        print("\n--- RESULTS ---")
        print(f"Work (A): Base={model.work_base}, Quota={model.work_quota}, Perceptors={model.work_perceptors}")
        print(f"Pros (G): Base={model.pro_base}, Quota={model.pro_quota}, Perceptors={model.pro_perceptors}")
        print(f"TOTAL: {model.total_quota}")
        
        # 4. Assertions (Flexible due to persistent DB)
        assert model.work_quota >= Decimal("300.00"), f"Work Quota mismatch: {model.work_quota}"
        assert model.pro_quota >= Decimal("150.00"), f"Pro Quota mismatch: {model.pro_quota}"
        assert model.total_quota >= Decimal("450.00"), f"Total mismatch: {model.total_quota}"
        
        print("\n[VERIFICATION PASSED]")
        
    except Exception as e:
        print(f"\n[FAILED]: {e}")
        import traceback
        traceback.print_exc()
    # finally:
        # db.close()

if __name__ == "__main__":
    verify_model_111()
