from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.job import Job
from app.models.application import Application
from app.schemas.job import JobCreate, JobUpdate
from app.schemas.application import ApplicationCreate
from app.services.email_service import send_application_confirmation_email
import threading


def auto_close_expired(job: Job) -> Job:
    if job.status == "ACTIVE" and job.last_date_to_apply < date.today():
        job.status = "CLOSED"
    return job


def create_job(db: Session, job_in: JobCreate, posted_by: int, company_id: str | None = None, company_name: str | None = None) -> Job:
    if db.query(Job).filter(Job.job_code == job_in.job_code, Job.is_deleted == False).first():
        raise HTTPException(status_code=400, detail="Job code already exists")

    job = Job(
        job_code=job_in.job_code,
        company_name=job_in.company_name or company_name,
        job_title=job_in.job_title,
        department=job_in.department,
        employment_type=job_in.employment_type,
        work_mode=job_in.work_mode,
        experience=job_in.experience,
        openings=job_in.openings,
        location=job_in.location,
        min_salary=job_in.min_salary,
        max_salary=job_in.max_salary,
        description=job_in.description,
        responsibilities=job_in.responsibilities,
        required_skills=job_in.required_skills,
        qualification=job_in.qualification,
        application_email=job_in.application_email,
        application_deadline=job_in.application_deadline,
        role=job_in.role,
        status=job_in.status or "Active",
        posted_by=posted_by,
        company_id=company_id,
        is_deleted=False,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_jobs(db: Session, skip: int, limit: int, active_only: bool = False):
    query = db.query(Job).filter(Job.is_deleted == False)
    if active_only:
        query = query.filter(Job.status == "ACTIVE")
    jobs = query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()
    # Auto-close expired jobs on read
    for job in jobs:
        if auto_close_expired(job).status == "CLOSED":
            db.commit()
    return jobs


def get_job_by_id(db: Session, job_id: int) -> Job:
    job = db.query(Job).filter(Job.id == job_id, Job.is_deleted == False).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    auto_close_expired(job)
    db.commit()
    db.refresh(job)
    return job


def update_job(db: Session, job_id: int, job_in: JobUpdate, current_user) -> Job:
    job = get_job_by_id(db, job_id)
    if current_user.role != "SUPER_ADMIN" and job.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="You can only edit jobs for your own company")

    data = job_in.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(job, key, value)

    db.commit()
    db.refresh(job)
    return job


def delete_job(db: Session, job_id: int, current_user):
    job = get_job_by_id(db, job_id)
    if current_user.role != "SUPER_ADMIN" and job.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="You can only delete jobs for your own company")
    job.is_deleted = True
    db.commit()


def apply_for_job(db: Session, job_id: int, app_in: ApplicationCreate) -> Application:
    job = get_job_by_id(db, job_id)

    if job.last_date_to_apply < date.today():
        raise HTTPException(status_code=400, detail="Job application deadline has expired")

    if job.status == "CLOSED":
        raise HTTPException(status_code=400, detail="This job is no longer accepting applications")

    existing = db.query(Application).filter(
        Application.job_id == job_id,
        Application.email == app_in.email
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already applied for this job")

    application = Application(
        job_id=job_id,
        first_name=app_in.firstName,
        last_name=app_in.lastName,
        email=app_in.email,
        mobile_number=app_in.mobileNumber,
        current_location=app_in.currentLocation,
        region=app_in.region,
        current_ctc=app_in.currentCtc,
        expected_ctc=app_in.expectedCtc,
        notice_period=app_in.noticePeriod,
        relevant_experience=app_in.releventExperience,
        resume_url=app_in.resume,
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    # Send confirmation email in background so it doesn't slow down the response
    threading.Thread(
        target=send_application_confirmation_email,
        args=(application.email, application.first_name, job.job_code, job.role)
    ).start()

    return application


def get_applicants_for_job(db: Session, job_id: int) -> list:
    get_job_by_id(db, job_id)
    return db.query(Application).filter(Application.job_id == job_id).all()


def get_all_applicants(db: Session) -> list:
    return db.query(Application).order_by(Application.applied_at.desc()).all()


def get_applied_jobs(db: Session, email: str) -> list:
    return db.query(Application).filter(Application.email == email).all()
