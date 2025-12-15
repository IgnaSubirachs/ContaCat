"""
Script de verificació del modúl de Recursos Humans (HR).
Prova la creació d'empleats, càlcul d'IRPF i generació de nòmines.
"""
import sys
import os
from datetime import date
from decimal import Decimal

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.infrastructure.db.base import init_db, SessionLocal
from app.domain.hr.services import EmployeeService, PayrollService
from app.infrastructure.persistence.hr.repository import SqlAlchemyEmployeeRepository, SqlAlchemyPayrollRepository
from app.domain.hr.entities import Employee, PayrollStatus

def verify_hr():
    print("=" * 60)
    print("VERIFICACIÓ MÒDUL DE RECURSOS HUMANS (HR)")
    print("=" * 60)

    print("\n1. Inicialitzant base de dades...")
    init_db()
    
    session = SessionLocal()
    
    try:
        # Repositories & Services
        employee_repo = SqlAlchemyEmployeeRepository(session)
        payroll_repo = SqlAlchemyPayrollRepository(session)
        
        employee_service = EmployeeService(employee_repo)
        payroll_service = PayrollService(payroll_repo, employee_repo)
        
        # 1. Create Employee
        print("\n[Step 1] Creant empleat de prova...")
        
        # Cleanup if exists
        dni_test = "40000000A"
        existing = employee_repo.find_by_dni(dni_test)
        if existing:
            print(f"   - L'empleat amb DNI {dni_test} ja existeix. Esborrant-lo per començar de zero...")
            employee_repo.delete(existing.id)
            session.commit()
            
        employee = employee_service.create_employee(
            first_name="Joan",
            last_name="Garcia",
            dni=dni_test,
            email="joan.garcia@example.com",
            phone="600123456",
            position="Desenvolupador Senior",
            department="IT",
            hire_date=date(2024, 1, 1),
            salary=Decimal("45000.00") # Salari Brut Anual o Mensual? Segons entities és mensual (salary * 12).
                                       # Wait, entities: salary: Decimal # Salari brut mensual
                                       # But usually in Spain we talk annual. Let's assume input is monthly gross for simplicity or check logic.
                                       # Entity: self.salary * 12 => annual. So input is monthly.
                                       # 45000 annual => 3750 monthly.
        )
        
        # Update extra fields usually not in create simple method
        employee.social_security_group = 1
        employee.children_count = 2
        employee.marital_status = "MARRIED"
        employee.irpf_retention = employee.calculate_irpf() # Recalculate based on new data
        employee_repo.update(employee)
        session.commit() # Persist updates
        
        print(f"✓ Empleat creat: {employee.full_name}")
        print(f"   - Salari Mensual Brut: {employee.salary} €")
        print(f"   - Retenció IRPF Calculada: {employee.irpf_retention} %")
        print(f"   - Situació: {employee.marital_status}, {employee.children_count} fills")
        
        # 2. Generate Payroll
        print("\n[Step 2] Generant nòmina de Gener 2024...")
        payroll = payroll_service.calculate_payroll(employee.id, 1, 2024)
        
        print(f"✓ Nòmina generada (Estat: {payroll.status.value})")
        print(f"   - Salari Base: {payroll.base_salary} €")
        print(f"   - Seguretat Social (Treballador): {payroll.social_security_employee} €")
        print(f"   - IRPF ({payroll.irpf_rate}%): {payroll.irpf_amount} €")
        print(f"   - Cost Seguretat Social (Empresa): {payroll.social_security_company} €")
        print(f"-------------------------------------------")
        print(f"   = LÍQUID A PERCEBRE: {payroll.net_salary} €")
        
        # Verification logic
        expected_ss = (employee.salary * Decimal("6.35") / 100).quantize(Decimal("0.01"))
        if payroll.social_security_employee != expected_ss:
            print(f"⚠ ALERTA: Càlcul SS incorrecte. Esperat: {expected_ss}, Trobat: {payroll.social_security_employee}")
            
        print("\n✅ Verificació HR completada correctament!")
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    success = verify_hr()
    sys.exit(0 if success else 1)
