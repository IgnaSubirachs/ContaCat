import sys
import os
from datetime import date
from decimal import Decimal

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.infrastructure.db.base import SessionLocal, init_db
from app.infrastructure.persistence.hr.repository import SqlAlchemyEmployeeRepository, SqlAlchemyPayrollRepository
from app.domain.hr.services import EmployeeService, PayrollService
from app.domain.hr.social_security import SocialSecurityCalculator

def run_verification():
    print("[INFO] Iniciant Injeccio de Dependencies per Test HR...")
    
    # 1. Repositories
    db_session = SessionLocal
    employee_repo = SqlAlchemyEmployeeRepository(db_session)
    payroll_repo = SqlAlchemyPayrollRepository(db_session)

    # 2. Services
    employee_service = EmployeeService(employee_repo)
    payroll_service = PayrollService(payroll_repo, employee_repo)
    
    # 3. Create Employee
    # Group 1 (Enginyers), Salary 3000/month
    # DNI must be valid-ish (or mock validator if needed). Assuming Validator checks format.
    # Using a known valid DNI generator or static one? 
    # Let's use a "fake" valid one if validation is strict.
    # Or rely on bypass if in test env? Validation logic: DocumentValidator.validate_document
    # Let's try to create one.
    
    print("[INFO] Creant Empleat de Prova...")
    # Clean up if exists (by email/dni)
    # Valid Spanish DNI: 12345678Z
    test_dni = "12345678Z"
    existing = employee_repo.find_by_dni(test_dni)
    if existing:
        print("[INFO] Eliminant empleat existent...")
        employee_repo.delete(existing.id)

    try:
        employee = employee_service.create_employee(
            first_name="Test",
            last_name="Engineer",
            dni=test_dni,
            email="test.hr@example.com",
            phone="600123456",
            position="Senior Engineer",
            department="IT",
            hire_date=date.today(),
            salary=Decimal("3000.00") # 3000 Gross Monthly
        )
        # Set extra fields
        employee.social_security_group = 1
        employee.children_count = 0
        employee.irpf_retention = Decimal("15.00") # Fixed for test simplicity
        employee_service._repository.update(employee)
        
        print(f"[OK] Empleat creat: {employee.full_name} (ID: {employee.id})")
        
    except ValueError as e:
        print(f"[ERROR] Error creant empleat: {e}")
        return

    # 4. Generate Payroll
    print("[INFO] Generant Nomina (Mes 1, 2025)...")
    payroll = payroll_service.calculate_payroll(employee.id, 1, 2025)
    
    print(f"[INFO] Nomina Generada: {payroll.gross_salary} Brut")
    
    # 5. Verify Calculations
    print("[INFO] Verificant Calculs...")
    
    # Expected SS (Group 1, 3000 base)
    # Common (4.7%): 141.00
    # Unemp (1.55%): 46.50
    # FP (0.1%): 3.00
    # Total Worker SS: 190.50
    
    expected_ss_worker = Decimal("190.50")
    
    # Expected IRPF (15%)
    expected_irpf = Decimal("450.00")
    
    # Expected Net
    # 3000 - 190.50 - 450.00 = 2359.50
    expected_net = Decimal("2359.50")
    
    if abs(payroll.social_security_employee - expected_ss_worker) < Decimal("0.05"):
        print(f"[SUCCESS] SS Treballador correcte: {payroll.social_security_employee}")
    else:
        print(f"[FAILURE] SS Treballador incorrecte. Esperat {expected_ss_worker}, Rebut {payroll.social_security_employee}")

    if abs(payroll.irpf_amount - expected_irpf) < Decimal("0.05"):
        print(f"[SUCCESS] IRPF correcte: {payroll.irpf_amount}")
    else:
        print(f"[FAILURE] IRPF incorrecte. Esperat {expected_irpf}, Rebut {payroll.irpf_amount}")

    if abs(payroll.net_salary - expected_net) < Decimal("0.05"):
        print(f"[SUCCESS] Net a Percebre correcte: {payroll.net_salary}")
    else:
        print(f"[FAILURE] Net incorrecte. Esperat {expected_net}, Rebut {payroll.net_salary}")

if __name__ == "__main__":
    try:
        run_verification()
    except Exception as e:
        print(f"[ERROR] EXCEPCIO: {e}")
        import traceback
        traceback.print_exc()
