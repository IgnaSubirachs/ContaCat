from fastapi import APIRouter, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
from datetime import date
from decimal import Decimal

from app.infrastructure.db.base import SessionLocal
from app.domain.hr.services import EmployeeService, PayrollService
from app.infrastructure.persistence.hr.repository import SqlAlchemyEmployeeRepository, SqlAlchemyPayrollRepository

router = APIRouter(prefix="/hr", tags=["hr"])
from app.interface.api.templates import templates

def get_hr_services():
    """Dependency to get HR services."""
    employee_repo = SqlAlchemyEmployeeRepository(SessionLocal)
    payroll_repo = SqlAlchemyPayrollRepository(SessionLocal)
    
    employee_service = EmployeeService(employee_repo)
    payroll_service = PayrollService(payroll_repo, employee_repo)
    
    return employee_service, payroll_service

@router.get("/employees", response_class=HTMLResponse)
async def list_employees(request: Request):
    """List all employees."""
    employee_service, _ = get_hr_services()
    employees = employee_service.list_all_employees()
    
    return templates.TemplateResponse("hr/employees/list.html", {
        "request": request,
        "employees": employees
    })

@router.get("/employees/new", response_class=HTMLResponse)
async def new_employee_form(request: Request):
    """Show create employee form."""
    return templates.TemplateResponse("hr/employees/create.html", {
        "request": request
    })

@router.post("/employees/create")
async def create_employee(
    first_name: str = Form(...),
    last_name: str = Form(...),
    dni: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    position: str = Form(...),
    department: str = Form(...),
    salary: float = Form(...), # Gross Annual or Monthly? domain expects monthly
    ss_group: int = Form(1),
    children_count: int = Form(0)
):
    """Create a new employee."""
    employee_service, _ = get_hr_services()
    try:
        # Create user
        emp = employee_service.create_employee(
            first_name=first_name,
            last_name=last_name,
            dni=dni,
            email=email,
            phone=phone,
            position=position,
            department=department,
            hire_date=date.today(),
            salary=Decimal(str(salary))
        )
        
        # Update extra fields not in create_employee signature but needed
        emp.social_security_group = ss_group
        emp.children_count = children_count
        # Recalculate IRPF with new family data
        emp.irpf_retention = emp.calculate_irpf()
        employee_service._repository.update(emp)

        return RedirectResponse(url="/hr/employees", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/payroll", response_class=HTMLResponse)
async def list_payrolls(request: Request, employee_id: Optional[str] = None):
    """List payrolls."""
    employee_service, payroll_service = get_hr_services()
    
    if employee_id:
        payrolls = payroll_service.list_by_employee(employee_id)
    else:
        # Get all payrolls via repo if method exists, else empty or specific logic
        # For now, let's assume we want to see everything or filter.
        # But crucially, we need the employees list for the modal dropdown.
        pass
        
    # Temporary: fetch all employees for the dropdown
    all_employees = employee_service.list_active_employees()
    
    # If payrolls not defined yet (because of else block above)
    try:
        if not employee_id:
             # If repository doesn't have list_all_payrolls, we might show empty or implement it.
             # Checking Service... it lacks list_all(). 
             # Let's just return empty list for now if no filter, or all if feasible.
             payrolls = [] 
    except:
        payrolls = []

    return templates.TemplateResponse("hr/payroll/list.html", {
        "request": request,
        "payrolls": payrolls,
        "employees": all_employees # Added this
    })

@router.post("/payroll/generate")
async def generate_payroll(
    employee_id: str = Form(...),
    month: int = Form(...),
    year: int = Form(...)
):
    """Generate payroll for an employee."""
    _, payroll_service = get_hr_services()
    try:
        payroll = payroll_service.calculate_payroll(employee_id, month, year)
        return RedirectResponse(url=f"/hr/payroll/{payroll.id}", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/payroll/{payroll_id}", response_class=HTMLResponse)
async def view_payroll(request: Request, payroll_id: str):
    """View payroll details."""
    _, payroll_service = get_hr_services()
    payroll = payroll_service.get_payroll(payroll_id)
    
    if not payroll:
        raise HTTPException(status_code=404, detail="Nòmina no trobada")
        
    return templates.TemplateResponse("hr/payroll/view.html", {
        "request": request,
        "payroll": payroll
    })

from fastapi import Response
from app.domain.documents.services import DocumentService

@router.get("/payroll/{payroll_id}/pdf")
async def get_payroll_pdf(payroll_id: str):
    """Generate and download PDF for payroll."""
    _, payroll_service = get_hr_services()
    payroll = payroll_service.get_payroll(payroll_id)
    
    if not payroll:
        raise HTTPException(status_code=404, detail="Nòmina no trobada")
    
    # Get Company Settings
    from app.infrastructure.db.base import SessionLocal
    from app.infrastructure.persistence.settings.repository import SqlAlchemyCompanySettingsRepository
    from app.domain.settings.services import SettingsService
    
    settings_repo = SqlAlchemyCompanySettingsRepository(SessionLocal)
    settings_service = SettingsService(settings_repo)
    settings = settings_service.get_settings_or_default()

    # Render template
    template = templates.get_template("hr/payroll/pdf.html")
    html_content = template.render({
        "payroll": payroll,
        "company": settings,
        "request": None
    })
    
    # Generate PDF
    doc_service = DocumentService()
    pdf_bytes = doc_service.generate_pdf(html_content)
    
    filename = f"Nomina_{payroll.year}_{payroll.month}_{payroll.employee.dni}.pdf"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
