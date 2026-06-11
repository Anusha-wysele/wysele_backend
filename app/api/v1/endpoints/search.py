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
            {"id": u.id, "name": f"{u.first_name} {u.last_name}",
             "email": u.email, "role": u.role, "employee_id": u.employee_id}
            for u in db.query(User).filter(
                User.role.in_(["ADMIN", "SUPER_ADMIN"]),
                (User.first_name.ilike(keyword)) |
                (User.last_name.ilike(keyword)) |
                (User.email.ilike(keyword)) |
                (User.employee_id.ilike(keyword))
            ).all()
        ]

        results["blogs"] = [
            {"id": b.id, "title": b.title, "category": b.category}
            for b in db.query(Blog).filter(
                Blog.title.ilike(keyword) | Blog.content.ilike(keyword) | Blog.category.ilike(keyword)
            ).all()
        ]

        results["jobs"] = [
            {"id": j.id, "role": j.role, "title": j.title, "job_code": j.job_code,
             "location": j.location, "status": j.status}
            for j in db.query(Job).filter(
                Job.is_deleted == False,
                Job.title.ilike(keyword) | Job.role.ilike(keyword) | Job.location.ilike(keyword) |
                Job.region.ilike(keyword) | Job.job_code.ilike(keyword)
            ).all()
        ]

        results["applications"] = [
            {"id": a.id, "name": f"{a.first_name} {a.last_name}",
             "email": a.email, "job_id": a.job_id}
            for a in db.query(Application).filter(
                Application.first_name.ilike(keyword) |
                Application.last_name.ilike(keyword) |
                Application.email.ilike(keyword)
            ).all()
        ]

        results["contacts"] = [
            {"id": c.id, "full_name": c.full_name, "email": c.email}
            for c in db.query(ContactInquiry).filter(
                ContactInquiry.full_name.ilike(keyword) | ContactInquiry.email.ilike(keyword)
            ).all()
        ]

        results["consulting"] = [
            {"id": c.id, "name": c.name, "email": c.email, "company_name": c.company_name}
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
                {"id": b.id, "title": b.title, "category": b.category}
                for b in db.query(Blog).filter(
                    Blog.title.ilike(keyword) | Blog.content.ilike(keyword) | Blog.category.ilike(keyword)
                ).all()
            ]

        if current_user.can_access_contact:
            results["contacts"] = [
                {"id": c.id, "full_name": c.full_name, "email": c.email}
                for c in db.query(ContactInquiry).filter(
                    ContactInquiry.full_name.ilike(keyword) | ContactInquiry.email.ilike(keyword)
                ).all()
            ]

        if current_user.can_access_consulting:
            results["consulting"] = [
                {"id": c.id, "name": c.name, "email": c.email, "company_name": c.company_name}
                for c in db.query(ConsultingInquiry).filter(
                    ConsultingInquiry.name.ilike(keyword) |
                    ConsultingInquiry.email.ilike(keyword) |
                    ConsultingInquiry.company_name.ilike(keyword)
                ).all()
            ]

        # Admins can search their own company's jobs and applications
        results["jobs"] = [
            {"id": j.id, "role": j.role, "title": j.title, "job_code": j.job_code,
             "location": j.location, "status": j.status}
            for j in db.query(Job).filter(
                Job.is_deleted == False,
                Job.company_id == current_user.company_id,
                (Job.title.ilike(keyword) | Job.role.ilike(keyword) | Job.location.ilike(keyword) |
                 Job.region.ilike(keyword) | Job.job_code.ilike(keyword))
            ).all()
        ]
        
        job_ids = [j["id"] for j in results["jobs"]]
        if job_ids:
            results["applications"] = [
                {"id": a.id, "name": f"{a.first_name} {a.last_name}",
                 "email": a.email, "job_id": a.job_id}
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
