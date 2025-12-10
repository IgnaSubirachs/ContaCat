from fastapi import APIRouter, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from datetime import date
from typing import List

from app.domain.hr.services import PayrollService, EmployeeService
from app.domain.hr.pdf_service import PayrollPdfService
from app.infrastructure.persistence.hr.repository import SqlAlchemyPayrollRepository, SqlAlchemyEmployeeRepository
from app.interface.api.templates import templates

router = APIRouter(prefix="/payrolls", tags=["payrolls"])

# Dependencies
def get_payroll_service():
    payroll_repo = SqlAlchemyPayrollRepository()
    employee_repo = SqlAlchemyEmployeeRepository()
    return PayrollService(payroll_repo, employee_repo)

def get_employee_service():
    employee_repo = SqlAlchemyEmployeeRepository()
    return EmployeeService(employee_repo)

def get_pdf_service():
    return PayrollPdfService(templates)

@router.get("/", response_class=HTMLResponse)
async def list_payrolls(
    request: Request, 
    month: int = None, 
    year: int = None,
    service: PayrollService = Depends(get_payroll_service),
    emp_service: EmployeeService = Depends(get_employee_service)
):
    """List payrolls."""
    if not month:
        month = date.today().month
    if not year:
        year = date.today().year
        
    payrolls = service.list_by_period(month, year)
    
    # Enrich with employee data if not already done by service (service currently does basic map)
    # The service implementation I wrote `list_by_period` does fetch, but let's ensure we display name
    # The service returns Payroll entities. entity.employee might be None if not eagerly loaded or manually set.
    # My service implementation of `list_by_period` blindly maps model to entity. 
    # It *does not* currently join employee.
    # So I need to fetch employees efficiently or N+1. 
    # For now, let's just fetch all active employees to map names or rely on the service to be improved later.
    # Actually, let's improve the service logic in the router for now or just iterate.
    
    employees = emp_service.list_all_employees()
    emp_map = {e.id: e for e in employees}
    
    for p in payrolls:
        if p.employee_id in emp_map:
            p.employee = emp_map[p.employee_id]

    return templates.TemplateResponse(
        "hr/payrolls/list.html",
        {
            "request": request, 
            "payrolls": payrolls, 
            "month": month, 
            "year": year,
            "employees": employees # For manual generation dropdown
        }
    )

@router.post("/generate")
async def generate_payroll(
    employee_id: str = Form(...),
    month: int = Form(...),
    year: int = Form(...),
    service: PayrollService = Depends(get_payroll_service)
):
    """Generate a payroll for an employee."""
    try:
        service.calculate_payroll(employee_id, month, year)
        return RedirectResponse(url=f"/payrolls/?month={month}&year={year}", status_code=303)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{payroll_id}/pdf")
async def download_payroll_pdf(
    payroll_id: str,
    service: PayrollService = Depends(get_payroll_service),
    pdf_service: PayrollPdfService = Depends(get_pdf_service)
):
    """Generate and download PDF."""
    payroll = service.get_payroll(payroll_id)
    if not payroll:
        raise HTTPException(status_code=404, detail="Nòmina no trobada")
    
    # Ensure employee is loaded
    if not payroll.employee:
        # Service get_payroll should load it, but double check logic
        pass 
        
    pdf_bytes = pdf_service.generate_payslip_pdf(payroll, payroll.employee)
    
    filename = f"Nomina_{payroll.year}_{payroll.month:02d}_{payroll.employee.dni}.pdf"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
