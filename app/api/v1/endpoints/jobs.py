from fastapi import APIRouter, Depends, Query, status, HTTPException, UploadFile, File, Form, BackgroundTasks, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_
import base64
import random
import string
from datetime import datetime, timedelta, timezone
from app.api import deps
from app.models.job import Job
from app.models.application import Application
from app.models.email_verification import EmailVerification
from app.models.user import User
from app.schemas.job import JobCreate, JobUpdate, JobResponse, JobCreateSuccess
from app.schemas.application import ApplicationCreate, ApplicationResponse, ApplicationSuccess
from app.schemas.consulting import OTPRequest
from app.schemas.pagination import PaginatedResponse, paginate
from app.services import job_service
from app.services.email_service import send_otp_email
from typing import List

router = APIRouter()

PURPOSE = "job_application"


def _generate_otp() -> str:
    return "".join(random.choices(string.digits, k=6))


# POST /jobs/send-otp — Public
@router.post("/send-otp")
def send_application_otp(body: OTPRequest, background_tasks: BackgroundTasks, db: Session = Depends(deps.get_db)):
    otp = _generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    db.query(EmailVerification).filter(
        EmailVerification.email == body.email,
        EmailVerification.purpose == PURPOSE,
        EmailVerification.is_verified == False
    ).delete()
    db.commit()

    db.add(EmailVerification(email=body.email, otp=otp, purpose=PURPOSE, is_verified=False, expires_at=expires_at))
    db.commit()

    background_tasks.add_task(send_otp_email, email_to=body.email, otp=otp, purpose=PURPOSE)
    return {"message": "OTP sent to your email. It expires in 10 minutes."}


# POST /jobs/apply — Public
@router.post("/apply", response_model=ApplicationSuccess, status_code=status.HTTP_201_CREATED)
def apply_for_job(
    otp: str = Query(..., description="OTP received on email"),
    job_id: int = Form(...),
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
    record = db.query(EmailVerification).filter(
        EmailVerification.email == email,
        EmailVerification.purpose == PURPOSE,
        EmailVerification.is_verified == False,
        EmailVerification.otp == otp
    ).order_by(EmailVerification.created_at.desc()).first()

    if not record:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    if datetime.now(timezone.utc) > record.expires_at:
        raise HTTPException(status_code=400, detail="OTP has expired. Please request a new one")

    ext = resume.filename.rsplit(".", 1)[-1].lower() if "." in resume.filename else ""
    if ext not in ("pdf", "docx"):
        raise HTTPException(status_code=400, detail="Resume must be a PDF or DOCX file")

    content = resume.file.read()
    encoded = base64.b64encode(content).decode()
    resume_data_url = f"data:application/{ext};base64,{encoded}"

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
        expectedCtc=expectedCtc,
    )
    result = job_service.apply_for_job(db, job_id, app_in)
    db.delete(record)
    db.commit()
    return {"message": "Application submitted successfully", "application": result}


from app.services.audit_service import log_audit_event
from typing import Optional, List

# Helper to check user optional (distinguishes Candidate vs Admin Portal calls)
async def get_current_user_optional(request: Request, db: Session = Depends(deps.get_db)) -> Optional[User]:
    try:
        return await deps.get_current_user(request, db)
    except Exception:
        return None


# POST /jobs — Admin/Super Admin
@router.post("/", response_model=JobCreateSuccess, status_code=status.HTTP_201_CREATED)
def create_job(
    job_in: JobCreate,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin)
):
    if current_user.role == "SUPER_ADMIN":
        company_id = job_in.company_id or "WYSELE"
        company_name = job_in.company_name or "WYSELE"
    else:
        company_id = current_user.company_id
        company_name = current_user.company_name

    job = job_service.create_job(
        db, job_in, current_user.id, company_id=company_id, company_name=company_name
    )

    # Log job creation
    log_audit_event(
        db,
        action="JOB_CREATION",
        user_id=current_user.id,
        email=current_user.email,
        details={
            "job_id": job.id,
            "job_code": job.job_code,
            "company_id": company_id,
            "company_name": company_name
        },
        ip_address=request.client.host if request.client else None
    )
    return {"message": "Job posted successfully", "job": job}


# GET /jobs/search/optimized — Optimized public search using single query keyword
@router.get("/search/optimized", response_model=PaginatedResponse[JobResponse])
def search_jobs_optimized(
    q: str = Query(..., min_length=1, description="Unified search keyword"),
    db: Session = Depends(deps.get_db),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100)
):
    keyword = f"%{q}%"
    conditions = [
        Job.title.ilike(keyword),
        Job.role.ilike(keyword),
        Job.location.ilike(keyword),
        Job.region.ilike(keyword),
        Job.description.ilike(keyword),
        Job.job_code.ilike(keyword)
    ]
    if q.strip().isdigit():
        conditions.append(Job.id == int(q.strip()))

    query = db.query(Job).filter(
        Job.is_deleted == False,
        Job.status == "ACTIVE",
        or_(*conditions)
    )
    return paginate(query.order_by(Job.created_at.desc()), page, limit)


# GET /jobs/search — Public search
@router.get("/search", response_model=PaginatedResponse[JobResponse])
def search_jobs(
    db: Session = Depends(deps.get_db),
    role: str = Query(default=None),
    title: str = Query(default=None),
    region: str = Query(default=None),
    location: str = Query(default=None),
    skills: str = Query(default=None, description="Comma separated e.g. Python,FastAPI"),
    experience: str = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100)
):
    query = db.query(Job).filter(Job.is_deleted == False, Job.status == "ACTIVE")
    if role:
        query = query.filter(Job.role.ilike(f"%{role}%"))
    if title:
        query = query.filter(Job.title.ilike(f"%{title}%"))
    if region:
        query = query.filter(Job.region.ilike(f"%{region}%"))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if experience:
        query = query.filter(Job.experience.ilike(f"%{experience}%"))
    if skills:
        for skill in [s.strip() for s in skills.split(",")]:
            query = query.filter(Job.key_skills.any(skill))
    return paginate(query.order_by(Job.created_at.desc()), page, limit)


# GET /jobs — Public Candidate or Multi-tenant Admin List
@router.get("/", response_model=PaginatedResponse[JobResponse])
def get_jobs(
    db: Session = Depends(deps.get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    company_id: Optional[str] = Query(default=None)
):
    query = db.query(Job).filter(Job.is_deleted == False)
    if current_user:
        # Authenticated Admin Portal view: restrict to own company jobs
        if current_user.role == "SUPER_ADMIN":
            if company_id:
                query = query.filter(Job.company_id == company_id.upper())
        else:
            query = query.filter(Job.company_id == current_user.company_id)
    else:
        # Public Candidate list: view active jobs only
        query = query.filter(Job.status == "ACTIVE")

    return paginate(query.order_by(Job.created_at.desc()), page, limit)


# GET /jobs/{id} — Public details
@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    job = job_service.get_job_by_id(db, job_id)
    if job.status == "DRAFT" and not current_user:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


# PUT /jobs/{id} — Admin/Super Admin
@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_in: JobUpdate,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin)
):
    job = job_service.get_job_by_id(db, job_id)
    if current_user.role != "SUPER_ADMIN" and job.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="You can only edit jobs for your own company")

    updated_job = job_service.update_job(db, job_id, job_in, current_user)

    # Log job update
    log_audit_event(
        db,
        action="JOB_UPDATE",
        user_id=current_user.id,
        email=current_user.email,
        details={
            "job_id": job_id,
            "job_code": updated_job.job_code,
            "company_id": updated_job.company_id
        },
        ip_address=request.client.host if request.client else None
    )

    return updated_job



# GET /jobs/{id}/applications — Admin/Super Admin
@router.get("/{job_id}/applications", response_model=List[ApplicationResponse])
def get_job_applications(
    job_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin)
):
    job = job_service.get_job_by_id(db, job_id)
    if current_user.role != "SUPER_ADMIN" and job.company_id != current_user.company_id:
        raise HTTPException(
            status_code=403,
            detail="You can only view applications for jobs belonging to your company"
        )
    return job_service.get_applicants_for_job(db, job_id)
