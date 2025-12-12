from typing import List, Optional
from datetime import date
from decimal import Decimal

from app.domain.hr.entities import Employee, Payroll, PayrollStatus
from app.domain.hr.repositories import EmployeeRepository, PayrollRepository
# ... imports ...


class EmployeeService:
    # ... existing code ...

    def delete_employee(self, employee_id: str) -> None:
        """Delete an employee."""
        employee = self._repository.find_by_id(employee_id)
        if not employee:
            raise ValueError(f"No s'ha trobat l'empleat amb ID {employee_id}")
        
        self._repository.delete(employee_id)


class PayrollService:
    """Service for managing payrolls."""
    
    def __init__(self, payroll_repository: PayrollRepository, employee_repository: EmployeeRepository):
        self._payroll_repository = payroll_repository
        self._employee_repository = employee_repository
    
    def calculate_payroll(self, employee_id: str, month: int, year: int) -> Payroll:
        """Calculate payroll for an employee for a specific month."""
        employee = self._employee_repository.find_by_id(employee_id)
        if not employee:
            raise ValueError(f"Employee not found: {employee_id}")
            
        # Check if already exists
        # In a real app we might check this, for now we assume we can recalculate/overwrite if needed
        # or create a new draft
        
        # 1. Base components
        # Assuming salary is monthly gross for 12 payments
        gross_salary = employee.salary
        base_salary = employee.base_salary
        supplements = employee.salary_supplements
        
        # If components sum doesn't match total salary, adjust base (simplification)
        if base_salary + supplements != gross_salary:
            # Fallback if detailed components not set
            base_salary = gross_salary
            supplements = Decimal("0")
            
        # 2. Social Security (General Regime 2024 approx)
        # Contingencias Comunes (4.7%) + Desempleo (1.55%) + FP (0.1%) = 6.35%
        ss_rate_employee = Decimal("6.35")
        ss_amount_employee = (gross_salary * ss_rate_employee / 100).quantize(Decimal("0.01"))
        
        # Company cost (approx 30-33%)
        ss_rate_company = Decimal("32.50") 
        ss_amount_company = (gross_salary * ss_rate_company / 100).quantize(Decimal("0.01"))
        
        # 3. IRPF
        irpf_rate = employee.irpf_retention
        irpf_amount = (gross_salary * irpf_rate / 100).quantize(Decimal("0.01"))
        
        # 4. Net
        net_salary = gross_salary - ss_amount_employee - irpf_amount
        
        # Create Payroll entity (DRAFT)
        payroll = Payroll(
            employee_id=employee.id,
            month=month,
            year=year,
            gross_salary=gross_salary,
            base_salary=base_salary,
            supplements=supplements,
            social_security_employee=ss_amount_employee,
            social_security_company=ss_amount_company,
            irpf_base=gross_salary,
            irpf_rate=irpf_rate,
            irpf_amount=irpf_amount,
            net_salary=net_salary,
            period_start=date(year, month, 1),
            period_end=self._get_last_day_of_month(month, year),
            working_days=30,
            status=PayrollStatus.DRAFT,
            employee=employee
        )
        
        # Save payload
        self._payroll_repository.add(payroll)
        return payroll
        
    def get_payroll(self, payroll_id: str) -> Optional[Payroll]:
        payroll = self._payroll_repository.find_by_id(payroll_id)
        if payroll:
            # Load employee
            payroll.employee = self._employee_repository.find_by_id(payroll.employee_id)
        return payroll

    def list_by_employee(self, employee_id: str) -> List[Payroll]:
        payrolls = self._payroll_repository.list_by_employee(employee_id)
        # Load employees
        # In optimized version this would be joinedload
        employee = self._employee_repository.find_by_id(employee_id)
        for p in payrolls:
            p.employee = employee
        return payrolls

    def _get_last_day_of_month(self, month: int, year: int) -> date:
        import calendar
        last_day = calendar.monthrange(year, month)[1]
        return date(year, month, last_day)


class EmployeeService:
    """Service for managing employees."""
    
    def __init__(self, repository: EmployeeRepository):
        self._repository = repository
    
    def create_employee(
        self,
        first_name: str,
        last_name: str,
        dni: str,
        email: str,
        phone: str,
        position: str,
        department: str,
        hire_date: date,
        salary: Decimal
    ) -> Employee:
        """Create a new employee."""
        # Check if DNI already exists
        existing = self._repository.find_by_dni(dni)
        if existing:
            raise ValueError(f"Ja existeix un empleat amb el DNI {dni}")
        
        # Create and validate employee
        employee = Employee(
            first_name=first_name,
            last_name=last_name,
            dni=dni,
            email=email,
            phone=phone,
            position=position,
            department=department,
            hire_date=hire_date,
            salary=salary,
            is_active=True
        )
        employee.validate()
        
        # Save to repository
        self._repository.add(employee)
        return employee
    
    def update_employee(
        self,
        employee_id: str,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        position: str,
        department: str,
        salary: Decimal
    ) -> Employee:
        """Update an existing employee."""
        employee = self._repository.find_by_id(employee_id)
        if not employee:
            raise ValueError(f"No s'ha trobat l'empleat amb ID {employee_id}")
        
        # Update fields
        employee.first_name = first_name
        employee.last_name = last_name
        employee.email = email
        employee.phone = phone
        employee.position = position
        employee.department = department
        employee.salary = salary
        
        employee.validate()
        self._repository.update(employee)
        return employee
    
    def deactivate_employee(self, employee_id: str) -> None:
        """Deactivate an employee."""
        employee = self._repository.find_by_id(employee_id)
        if not employee:
            raise ValueError(f"No s'ha trobat l'empleat amb ID {employee_id}")
        
        employee.is_active = False
        self._repository.update(employee)
    
    def list_all_employees(self) -> List[Employee]:
        """List all employees."""
        return self._repository.list_all()
    
    def list_active_employees(self) -> List[Employee]:
        """List only active employees."""
        return self._repository.list_active()
    
    def get_employee_by_id(self, employee_id: str) -> Optional[Employee]:
        """Get an employee by ID."""
        return self._repository.find_by_id(employee_id)
    
    def delete_employee(self, employee_id: str) -> None:
        """Delete an employee."""
        employee = self._repository.find_by_id(employee_id)
        if not employee:
            raise ValueError(f"No s'ha trobat l'empleat amb ID {employee_id}")
        
        self._repository.delete(employee_id)
