from fastapi import APIRouter
from app.api.v1.endpoints import auth, blogs, admins, contact, jobs, consulting

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(blogs.router, prefix="/blogs", tags=["Blogs"])
api_router.include_router(admins.router, prefix="/admins", tags=["Admins"])
api_router.include_router(contact.router, prefix="/contact", tags=["Contact"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(consulting.router, prefix="/consulting", tags=["Consulting"])