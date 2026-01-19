from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
import uuid

from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.user import User
from app.models.employee import EmployeeProfile
from app.schemas.employee import EmployeeCreate, EmployeeResponse, EmployeeUpdate, EmployeeProfileCreate
from app.models.company import Company
from app.models.rbac import Role

router = APIRouter()

@router.get("/test")
def test():
    return {"message": "ok employees"}

@router.get("/", response_model=List[EmployeeResponse])
async def get_employees(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List employees.
    """
    print(f"DEBUG: get_employees called by {current_user.email} (role: {current_user.role}, company: {current_user.company_id})")
    
    query = select(User).options(
        joinedload(User.employee_profile), 
        joinedload(User.pos_location)
    ).where(
        User.company_id == current_user.company_id,
        User.user_type.in_(['admin', 'manager', 'agent', 'receptionist']) # specific employee roles
    ).offset(skip).limit(limit)
    
    employees = db.execute(query).scalars().all()
    print(f"DEBUG: Found {len(employees)} employees")
    return employees

@router.post("/", response_model=EmployeeResponse)
def create_employee(
    employee_in: EmployeeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new employee.
    """
    # Check if user already exists
    stmt = select(User).where(User.email == employee_in.email)
    existing_user = db.execute(stmt).scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Use current user's company if not provided (which is likely)
    company_id = employee_in.company_id or current_user.company_id
    
    if not company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company ID is required to create an employee."
        )
    
    # Create User
    new_user = User(
        email=employee_in.email,
        password_hash=get_password_hash(employee_in.password),
        first_name=employee_in.first_name,
        last_name=employee_in.last_name,
        phone=employee_in.phone,
        role=employee_in.role,
        company_id=company_id,
        pos_location_id=employee_in.pos_location_id,
        created_by=employee_in.created_by or current_user.id,
        is_active=True,
        is_verified=True # Auto verify employees created by admin
    )
    db.add(new_user)
    db.flush() # Flush to get user ID
    
    # Create EmployeeProfile if data provided
    if employee_in.profile:
        new_profile = EmployeeProfile(
            user_id=new_user.id,
            payment_method=employee_in.profile.payment_method,
            mobile_money_provider=employee_in.profile.mobile_money_provider,
            mobile_money_number=employee_in.profile.mobile_money_number,
            bank_name=employee_in.profile.bank_name,
            bank_account_number=employee_in.profile.bank_account_number,
            bank_account_holder_name=employee_in.profile.bank_account_holder_name,
            iban=employee_in.profile.iban,
            swift_bic=employee_in.profile.swift_bic,
            job_title=employee_in.profile.job_title,
            department=employee_in.profile.department,
            base_salary=employee_in.profile.base_salary,
            currency=employee_in.profile.currency or 'XOF'
        )
        db.add(new_profile)
    
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get employee details.
    """
    stmt = select(User).options(
        joinedload(User.employee_profile), 
        joinedload(User.pos_location)
    ).where(User.id == employee_id, User.company_id == current_user.company_id)
    employee = db.execute(stmt).scalar_one_or_none()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    return employee

@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: uuid.UUID,
    employee_in: EmployeeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update employee details.
    """
    stmt = select(User).where(User.id == employee_id, User.company_id == current_user.company_id)
    employee = db.execute(stmt).scalar_one_or_none()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Update User fields
    if employee_in.first_name is not None:
        employee.first_name = employee_in.first_name
    if employee_in.last_name is not None:
        employee.last_name = employee_in.last_name
    if employee_in.phone is not None:
        employee.phone = employee_in.phone
    if employee_in.role is not None:
        employee.role = employee_in.role
    if employee_in.is_active is not None:
        employee.is_active = employee_in.is_active
    if employee_in.pos_location_id is not None:
        employee.pos_location_id = employee_in.pos_location_id
        
    # Update or Create Profile
    if employee_in.profile:
        # Check if profile exists
        if not employee.employee_profile:
            # Create new profile
            new_profile = EmployeeProfile(
                user_id=employee.id,
                payment_method=employee_in.profile.payment_method or "bank_transfer",
                mobile_money_provider=employee_in.profile.mobile_money_provider,
                mobile_money_number=employee_in.profile.mobile_money_number,
                bank_name=employee_in.profile.bank_name,
                bank_account_number=employee_in.profile.bank_account_number,
                bank_account_holder_name=employee_in.profile.bank_account_holder_name,
                job_title=employee_in.profile.job_title,
                department=employee_in.profile.department,
                base_salary=employee_in.profile.base_salary,
                currency=employee_in.profile.currency or 'XOF'
            )
            db.add(new_profile)
        else:
            # Update existing
            profile = employee.employee_profile
            if employee_in.profile.payment_method is not None:
                profile.payment_method = employee_in.profile.payment_method
            if employee_in.profile.mobile_money_provider is not None:
                profile.mobile_money_provider = employee_in.profile.mobile_money_provider
            if employee_in.profile.mobile_money_number is not None:
                profile.mobile_money_number = employee_in.profile.mobile_money_number
            if employee_in.profile.bank_name is not None:
                profile.bank_name = employee_in.profile.bank_name
            if employee_in.profile.bank_account_number is not None:
                profile.bank_account_number = employee_in.profile.bank_account_number
            if employee_in.profile.bank_account_holder_name is not None:
                profile.bank_account_holder_name = employee_in.profile.bank_account_holder_name
            if employee_in.profile.job_title is not None:
                profile.job_title = employee_in.profile.job_title
            if employee_in.profile.department is not None:
                profile.department = employee_in.profile.department
            if employee_in.profile.base_salary is not None:
                profile.base_salary = employee_in.profile.base_salary
            if employee_in.profile.currency is not None:
                profile.currency = employee_in.profile.currency

    db.commit()
    db.refresh(employee)
    return employee
