from fastapi import APIRouter, Depends, Query, status, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import base64, uuid
from app.api import deps
from app.models.user import User
from app.models.job import Job
from app.models.application import Application
from app.schemas.job import JobCreate, JobUpdate, JobResponse
from app.schemas.application import ApplicationCreate, ApplicationResponse
from app.schemas.pagination import PaginatedResponse, paginate
from app.services import job_service
from typing import List

router = APIRouter()


# POST /jobs — Admin or HR can create jobs
@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job_in: JobCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_hr_or_admin)
):
    return job_service.create_job(db, job_in, current_user.id)


# GET /jobs/search — Public search by role, region, skills, experience
@router.get("/search", response_model=PaginatedResponse[JobResponse])
def search_jobs(
    db: Session = Depends(deps.get_db),
    role: str = Query(default=None),
    region: str = Query(default=None),
    location: str = Query(default=None),
    skills: str = Query(default=None, description="Comma separated skills e.g. Python,FastAPI"),
    experience: str = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100)
):
    query = db.query(Job).filter(Job.is_deleted == False, Job.status == "ACTIVE")

    if role:
        query = query.filter(Job.role.ilike(f"%{role}%"))
    if region:
        query = query.filter(Job.region.ilike(f"%{region}%"))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if experience:
        query = query.filter(Job.experience.ilike(f"%{experience}%"))
    if skills:
        for skill in [s.strip() for s in skills.split(",")]:
            query = query.filter(Job.key_skills.any(skill))

    query = query.order_by(Job.created_at.desc())
    return paginate(query, page, limit)


# GET /jobs — Public (paginated, with optional category filter)
@router.get("/", response_model=PaginatedResponse[JobResponse])
def get_jobs(
    db: Session = Depends(deps.get_db),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100)
):
    query = db.query(Job).filter(Job.is_deleted == False).order_by(Job.created_at.desc())
    return paginate(query, page, limit)


# GET /jobs/{id} — Public
@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(deps.get_db)):
    return job_service.get_job_by_id(db, job_id)


# PUT /jobs/{id} — Admin or HR (owner or SUPER_ADMIN)
@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_in: JobUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_hr_or_admin)
):
    return job_service.update_job(db, job_id, job_in, current_user.id, current_user.role == "SUPER_ADMIN")


# DELETE /jobs/{id} — Admin or HR (owner or SUPER_ADMIN), soft delete
@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_hr_or_admin)
):
    job_service.delete_job(db, job_id, current_user.id, current_user.role == "SUPER_ADMIN")


# POST /jobs/{id}/apply — Public (applicants), multipart form with resume file
@router.post("/{job_id}/apply", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def apply_for_job(
    job_id: int,
    firstName: str = Form(...),
    lastName: str = Form(...),
    email: str = Form(...),
    mobileNumber: str = Form(...),
    currentLocation: str = Form(...),
    noticePeriod: str = Form(...),
    releventExperience: str = Form(...),
    resume: UploadFile = File(...),
    region: str = Form(None),
    currentCtc: str = Form(None),
    expectedCtc: str = Form(None),
    db: Session = Depends(deps.get_db)
):
    ext = resume.filename.rsplit(".", 1)[-1].lower() if "." in resume.filename else ""
    if ext not in ("pdf", "docx"):
        raise HTTPException(status_code=400, detail="Resume must be a PDF or DOCX file")

    content = resume.file.read()
    encoded = base64.b64encode(content).decode()
    resume_data_url = f"data:application/{ext};base64,{encoded}"

    from app.schemas.application import ApplicationCreate
    app_in = ApplicationCreate(
        firstName=firstName,
        lastName=lastName,
        email=email,
        mobileNumber=mobileNumber,
        currentLocation=currentLocation,
        noticePeriod=noticePeriod,
        releventExperience=releventExperience,
        resume=resume_data_url,
        region=region,
        currentCtc=currentCtc,
        expectedCtc=expectedCtc
    )
    return job_service.apply_for_job(db, job_id, app_in)


# GET /jobs/{id}/applications — Admin or HR only
@router.get("/{job_id}/applications", response_model=List[ApplicationResponse])
def get_job_applications(
    job_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_hr_or_admin)
):
    return job_service.get_applicants_for_job(db, job_id)

