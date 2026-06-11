from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.api import deps
from app.models.user import User
from app.core import security
from app.schemas.job import JobResponse
from app.schemas.application import ApplicationResponse
from app.schemas.pagination import PaginatedResponse, paginate
from app.schemas.user import UserCreate, UserResponse
from app.models.job import Job
from app.services import job_service
from fastapi import HTTPException

router = APIRouter()


# ADMIN: Create HR user
@router.post("/create-hr", response_model=UserResponse)
def create_hr(
    user_in: UserCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_super_admin)
):
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    if db.query(User).filter(User.employee_id == user_in.employee_id).first():
        raise HTTPException(status_code=400, detail="Employee ID already exists")

    from app.api.deps import normalize_company
    company_id, company_name = normalize_company(user_in.company_id)

    hr_user = User(
        email=user_in.email,
        employee_id=user_in.employee_id,
        hashed_password=security.get_password_hash(user_in.password),
        first_name=user_in.first_name,
        middle_name=user_in.middle_name,
        last_name=user_in.last_name,
        phone_number=user_in.phone_number,
        role="HR",
        company_id=company_id,
        company_name=company_name,
        is_active=True,
        created_by_id=current_user.id
    )
    db.add(hr_user)
    db.commit()
    db.refresh(hr_user)
    return hr_user


# ADMIN: Get all jobs (paginated)
@router.get("/jobs", response_model=PaginatedResponse[JobResponse])
def get_all_jobs(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_super_admin),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100)
):
    query = db.query(Job).filter(Job.is_deleted == False).order_by(Job.created_at.desc())
    return paginate(query, page, limit)


# ADMIN: Get all applicants across all jobs
@router.get("/applicants", response_model=List[ApplicationResponse])
def get_all_applicants(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_super_admin)
):
    return job_service.get_all_applicants(db)



# ADMIN: Get applicants for a specific job
@router.get("/job/{job_id}/applicants", response_model=List[ApplicationResponse])
def get_job_applicants(
    job_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_super_admin)
):
    return job_service.get_applicants_for_job(db, job_id)
