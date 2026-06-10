from fastapi import APIRouter, Depends
from app.api.v1.endpoints import auth, blogs, admins, contact, jobs, consulting, search, audit
from app.api import deps

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(blogs.router, prefix="/blogs", tags=["Blogs"])
api_router.include_router(admins.router, prefix="/admins", tags=["Admins"])
api_router.include_router(contact.router, prefix="/contact", tags=["Contact"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(consulting.router, prefix="/consulting", tags=["Consulting"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(audit.router, prefix="/audit", tags=["Audit"])