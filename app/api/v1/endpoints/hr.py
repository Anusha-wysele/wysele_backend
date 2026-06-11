from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.schemas.job import JobCreate, JobUpdate, JobResponse
from app.schemas.application import ApplicationResponse
from app.schemas.pagination import PaginatedResponse, paginate
from app.models.job import Job
from app.services import job_service
from typing import List, Optional

router = APIRouter()


# HR: Post a new job
@router.post("/jobs", response_model=JobResponse)
def create_job(
    job_in: JobCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_hr_or_admin)
):
    return job_service.create_job(db, job_in, current_user.id)


# HR: Get all jobs posted by this HR (paginated)
@router.get("/jobs", response_model=PaginatedResponse[JobResponse])
def get_hr_jobs(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_hr_or_admin),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    status: Optional[str] = Query(default=None)
):
    query = db.query(Job).filter(
        Job.posted_by == current_user.id,
        Job.is_deleted == False
    )
    if status:
        query = query.filter(Job.status == status.upper())
    return paginate(query.order_by(Job.created_at.desc()), page, limit)


# HR: Update own job
@router.put("/job/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_in: JobUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_hr_or_admin)
):
    return job_service.update_job(db, job_id, job_in, current_user)


# HR: Soft delete own job
@router.delete("/job/{job_id}", status_code=204)
def delete_job(
    job_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_hr_or_admin)
):
    job_service.delete_job(db, job_id, current_user)


# HR: Get applicants for a specific job
@router.get("/job/{job_id}/applicants", response_model=List[ApplicationResponse])
def get_job_applicants(
    job_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_hr_or_admin)
):
    return job_service.get_applicants_for_job(db, job_id)
