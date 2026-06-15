from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.blog import Blog
from app.models.job import Job
from app.models.application import Application
from app.models.contact import ContactInquiry
from app.models.consulting import ConsultingInquiry

router = APIRouter()


def serialize_blog(b):
    return {
        "id": b.id,
        "title": b.title,
        "content": b.content,
        "category": b.category,
        "image_url": b.image_url,
        "read_time": b.read_time,
        "status": b.status,
        "created_at": b.created_at.isoformat() if b.created_at else None,
        "author_id": b.author_id,
        "author_name": b.author_name
    }


def serialize_job(j):
    return {
        "id": j.id,
        "job_code": j.job_code,
        "company_name": j.company_name,
        "job_title": j.job_title,
        "department": j.department,
        "employment_type": j.employment_type,
        "work_mode": j.work_mode,
        "experience": j.experience,
        "openings": j.openings,
        "location": j.location,
        "min_salary": j.min_salary,
        "max_salary": j.max_salary,
        "description": j.description,
        "responsibilities": j.responsibilities,
        "required_skills": j.required_skills,
        "qualification": j.qualification,
        "application_email": j.application_email,
        "application_deadline": j.application_deadline.isoformat() if j.application_deadline else None,
        "job_posted_date": j.job_posted_date.isoformat() if j.job_posted_date else None,
        "role": j.role,
        "status": j.status,
        "company_id": j.company_id,
        "posted_by": j.posted_by,
        "is_deleted": j.is_deleted,
        "created_at": j.created_at.isoformat() if j.created_at else None,
        "updated_at": j.updated_at.isoformat() if j.updated_at else None
    }


def serialize_application(a):
    return {
        "id": a.id,
        "job_id": a.job_id,
        "first_name": a.first_name,
        "last_name": a.last_name,
        "email": a.email,
        "mobile_number": a.mobile_number,
        "current_location": a.current_location,
        "region": a.region,
        "current_ctc": a.current_ctc,
        "expected_ctc": a.expected_ctc,
        "notice_period": a.notice_period,
        "relevant_experience": a.relevant_experience,
        "resume_url": a.resume_url,
        "applied_at": a.applied_at.isoformat() if a.applied_at else None
    }


def serialize_contact(c):
    return {
        "id": c.id,
        "full_name": c.full_name,
        "email": c.email,
        "phone_number": c.phone_number,
        "location": c.location,
        "message": c.message,
        "company": c.company,
        "created_at": c.created_at.isoformat() if c.created_at else None
    }


def serialize_consulting(c):
    return {
        "id": c.id,
        "name": c.name,
        "email": c.email,
        "mobile_number": c.mobile_number,
        "company_name": c.company_name,
        "message": c.message,
        "company": c.company,
        "created_at": c.created_at.isoformat() if c.created_at else None
    }


@router.get("/")
def global_search(
    q: str = Query(..., min_length=1, description="Search keyword"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    results = {}
    keyword = f"%{q}%"

    # ── SUPER_ADMIN — sees everything ──────────────────────────────
    if current_user.role == "SUPER_ADMIN":

        results["users"] = [
            {
                "id": u.id,
                "emp_id": u.employee_id,
                "email": u.email,
                "name": u.name,
                "first_name": u.first_name,
                "middle_name": u.middle_name,
                "last_name": u.last_name,
                "phone_number": u.phone_number,
                "company_id": u.company_id,
                "company_name": u.company_name,
                "role": u.role,
                "is_active": u.is_active,
                "is_first_login": u.is_first_login,
                "can_post_blog": u.can_post_blog,
                "can_edit_blog": u.can_edit_blog,
                "can_delete_blog": u.can_delete_blog,
                "can_post_job": u.can_post_job,
                "can_access_contact": u.can_access_contact,
                "can_access_consulting": u.can_access_consulting,
                "created_at": u.created_at.isoformat() if u.created_at else None
            }
            for u in db.query(User).filter(
                User.role.in_(["ADMIN", "SUPER_ADMIN"]),
                (User.first_name.ilike(keyword)) |
                (User.last_name.ilike(keyword)) |
                (User.email.ilike(keyword)) |
                (User.employee_id.ilike(keyword))
            ).all()
        ]

        results["blogs"] = [
            serialize_blog(b)
            for b in db.query(Blog).filter(
                Blog.title.ilike(keyword) | Blog.content.ilike(keyword) | Blog.category.ilike(keyword)
            ).all()
        ]

        results["jobs"] = [
            serialize_job(j)
            for j in db.query(Job).filter(
                Job.is_deleted == False,
                Job.job_title.ilike(keyword) | Job.role.ilike(keyword) | Job.location.ilike(keyword) |
                Job.job_code.ilike(keyword) | Job.department.ilike(keyword) | Job.work_mode.ilike(keyword)
            ).all()
        ]

        results["applications"] = [
            serialize_application(a)
            for a in db.query(Application).filter(
                Application.first_name.ilike(keyword) |
                Application.last_name.ilike(keyword) |
                Application.email.ilike(keyword)
            ).all()
        ]

        results["contacts"] = [
            serialize_contact(c)
            for c in db.query(ContactInquiry).filter(
                ContactInquiry.full_name.ilike(keyword) | ContactInquiry.email.ilike(keyword)
            ).all()
        ]

        results["consulting"] = [
            serialize_consulting(c)
            for c in db.query(ConsultingInquiry).filter(
                ConsultingInquiry.name.ilike(keyword) |
                ConsultingInquiry.email.ilike(keyword) |
                ConsultingInquiry.company_name.ilike(keyword)
            ).all()
        ]

    # ── ADMIN — based on permissions & multi-tenancy ───────────────
    elif current_user.role == "ADMIN":

        if current_user.can_post_blog or current_user.can_edit_blog or current_user.can_delete_blog:
            results["blogs"] = [
                serialize_blog(b)
                for b in db.query(Blog).filter(
                    Blog.title.ilike(keyword) | Blog.content.ilike(keyword) | Blog.category.ilike(keyword)
                ).all()
            ]

        if current_user.can_access_contact:
            results["contacts"] = [
                serialize_contact(c)
                for c in db.query(ContactInquiry).filter(
                    ContactInquiry.full_name.ilike(keyword) | ContactInquiry.email.ilike(keyword)
                ).all()
            ]

        if current_user.can_access_consulting:
            results["consulting"] = [
                serialize_consulting(c)
                for c in db.query(ConsultingInquiry).filter(
                    ConsultingInquiry.name.ilike(keyword) |
                    ConsultingInquiry.email.ilike(keyword) |
                    ConsultingInquiry.company_name.ilike(keyword)
                ).all()
            ]

        # Admins can search their own company's jobs and applications
        results["jobs"] = [
            serialize_job(j)
            for j in db.query(Job).filter(
                Job.is_deleted == False,
                Job.company_id == current_user.company_id,
                (Job.job_title.ilike(keyword) | Job.role.ilike(keyword) | Job.location.ilike(keyword) |
                 Job.job_code.ilike(keyword) | Job.department.ilike(keyword) | Job.work_mode.ilike(keyword))
            ).all()
        ]
        
        job_ids = [j["id"] for j in results["jobs"]]
        if job_ids:
            results["applications"] = [
                serialize_application(a)
                for a in db.query(Application).filter(
                    Application.job_id.in_(job_ids),
                    (Application.first_name.ilike(keyword) |
                     Application.last_name.ilike(keyword) |
                     Application.email.ilike(keyword))
                ).all()
            ]

    return {
        "query": q,
        "results": results
    }
