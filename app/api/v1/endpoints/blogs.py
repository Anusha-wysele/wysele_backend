from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.orm import Session
from typing import Optional
from urllib.parse import urlparse
from app.api import deps
from app.models.blog import Blog
from app.models.user import User
from app.schemas.blog import BlogCreate, BlogUpdate, BlogResponse, BlogCreateSuccess
from app.schemas.pagination import PaginatedResponse, paginate

router = APIRouter()

BLOCKED_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "169.254.169.254"}


def validate_image_url(url: Optional[str]):
    if not url:
        return
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Invalid image URL scheme.")
    if parsed.hostname in BLOCKED_HOSTS:
        raise HTTPException(status_code=400, detail="Invalid image URL host.")


# Helper to check user optional
async def get_current_user_optional(request: Request, db: Session = Depends(deps.get_db)) -> Optional[User]:
    try:
        return await deps.get_current_user(request, db)
    except Exception:
        return None


# PUBLIC: Get all blogs
@router.get("/", response_model=PaginatedResponse[BlogResponse])
def get_blogs(
    db: Session = Depends(deps.get_db),
    category: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    query = db.query(Blog)
    if not current_user:
        query = query.filter(Blog.status == "ACTIVE")
    if category and category != "All":
        query = query.filter(Blog.category == category)
    return paginate(query.order_by(Blog.created_at.desc()), page, limit)


# PUBLIC: Get single blog
@router.get("/{blog_id}", response_model=BlogResponse)
def get_blog(
    blog_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog or (blog.status == "DRAFT" and not current_user):
        raise HTTPException(status_code=404, detail="Blog not found")
    return blog


# ADMIN with can_post_blog permission
@router.post("/", response_model=BlogCreateSuccess)
def create_blog(
    blog_in: BlogCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_can_post_blog)
):
    validate_image_url(blog_in.image_url)
    new_blog = Blog(**blog_in.model_dump())
    new_blog.author_id = current_user.id
    new_blog.author_name = current_user.name or f"{current_user.first_name} {current_user.last_name}"
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return {"message": "Blog posted successfully", "blog": new_blog}


# ADMIN with can_edit_blog permission
@router.put("/{blog_id}", response_model=BlogResponse)
def update_blog(
    blog_id: int,
    blog_in: BlogUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_can_edit_blog)
):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    if blog_in.image_url:
        validate_image_url(blog_in.image_url)
    for field, value in blog_in.model_dump(exclude_unset=True).items():
        setattr(blog, field, value)
    db.commit()
    db.refresh(blog)
    return blog


