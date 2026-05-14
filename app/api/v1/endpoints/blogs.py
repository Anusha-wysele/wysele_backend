from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from urllib.parse import urlparse
from app.api import deps
from app.models.blog import Blog
from app.models.user import User
from app.schemas.blog import BlogCreate, BlogUpdate, BlogResponse
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


# PUBLIC: Get all blogs
@router.get("/", response_model=PaginatedResponse[BlogResponse])
def get_blogs(
    db: Session = Depends(deps.get_db),
    category: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100)
):
    query = db.query(Blog)
    if category and category != "All":
        query = query.filter(Blog.category == category)
    return paginate(query.order_by(Blog.created_at.desc()), page, limit)


# PUBLIC: Get single blog
@router.get("/{blog_id}", response_model=BlogResponse)
def get_blog(blog_id: int, db: Session = Depends(deps.get_db)):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return blog


# ADMIN with can_post_blog permission
@router.post("/", response_model=BlogResponse)
def create_blog(
    blog_in: BlogCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_can_post_blog)
):
    validate_image_url(blog_in.image_url)
    new_blog = Blog(**blog_in.model_dump())
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


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


# ADMIN with can_delete_blog permission
@router.delete("/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blog(
    blog_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_can_delete_blog)
):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    db.delete(blog)
    db.commit()
