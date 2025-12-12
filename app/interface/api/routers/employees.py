from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import date
from decimal import Decimal
import os

from app.domain.hr.services import EmployeeService
from app.infrastructure.persistence.hr.repository import SqlAlchemyEmployeeRepository

# Initialize templates
from app.interface.api.templates import templates

# Initialize service
employee_repo = SqlAlchemyEmployeeRepository()
employee_service = EmployeeService(employee_repo)

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("/", response_class=HTMLResponse)
async def list_employees(request: Request, filter: str = "all"):
    """List all employees."""
    if filter == "active":
        employees = employee_service.list_active_employees()
    else:
        employees = employee_service.list_all_employees()
    
    return templates.TemplateResponse(
        "employees/list.html",
        {"request": request, "employees": employees, "filter": filter}
    )


@router.get("/create", response_class=HTMLResponse)
async def create_employee_form(request: Request):
    """Show create employee form."""
    return templates.TemplateResponse(
        "employees/create.html",
        {"request": request}
    )


@router.post("/create")
async def create_employee(
    first_name: str = Form(...),
    last_name: str = Form(...),
    dni: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    position: str = Form(...),
    department: str = Form(...),
    hire_date: str = Form(...),
    salary: str = Form(...),
):
    """Create a new employee."""
    try:
        # Parse date and salary
        hire_date_obj = date.fromisoformat(hire_date)
        salary_decimal = Decimal(salary)
        
        employee_service.create_employee(
            first_name=first_name,
            last_name=last_name,
            dni=dni,
            email=email,
            phone=phone,
            position=position,
            department=department,
            hire_date=hire_date_obj,
            salary=salary_decimal,
        )
        return RedirectResponse(url="/employees/", status_code=303)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{employee_id}", response_class=HTMLResponse)
async def employee_detail(request: Request, employee_id: str):
    """Show employee detail."""
    employee = employee_service.get_employee_by_id(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Empleat no trobat")
    
    return templates.TemplateResponse(
        "employees/detail.html",
        {"request": request, "employee": employee}
    )


@router.get("/edit/{employee_id}", response_class=HTMLResponse)
async def edit_employee_form(request: Request, employee_id: str):
    """Show edit employee form."""
    employee = employee_service.get_employee_by_id(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Empleat no trobat")
    
    return templates.TemplateResponse(
        "employees/edit.html",
        {"request": request, "employee": employee}
    )


@router.post("/edit/{employee_id}")
async def edit_employee(
    employee_id: str,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    position: str = Form(...),
    department: str = Form(...),
    salary: str = Form(...),
):
    """Update an employee."""
    try:
        salary_decimal = Decimal(salary)
        employee_service.update_employee(
            employee_id=employee_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            position=position,
            department=department,
            salary=salary_decimal,
        )
        return RedirectResponse(url="/employees/", status_code=303)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/delete/{employee_id}")
async def delete_employee(employee_id: str):
    """Delete an employee."""
    try:
        employee_service.delete_employee(employee_id)
        return RedirectResponse(url="/employees/", status_code=303)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# JSON API endpoints
@router.get("/api/list")
async def api_list_employees():
    """API endpoint to list all employees as JSON."""
    employees = employee_service.list_all_employees()
    return {
        "employees": [
            {
                "id": e.id,
                "first_name": e.first_name,
                "last_name": e.last_name,
                "full_name": e.full_name,
                "dni": e.dni,
                "email": e.email,
                "phone": e.phone,
                "position": e.position,
                "department": e.department,
                "hire_date": e.hire_date.isoformat(),
                "salary": str(e.salary),
                "is_active": e.is_active,
            }
            for e in employees
        ]
    }
