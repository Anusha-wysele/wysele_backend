from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api import deps
from app.models.audit import Audit
from app.schemas.audit import AuditResponse
from app.schemas.pagination import PaginatedResponse, paginate

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[AuditResponse])
def get_audit_logs(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_super_admin),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    action: Optional[str] = Query(default=None),
    email: Optional[str] = Query(default=None)
):
    query = db.query(Audit)
    if action:
        query = query.filter(Audit.action == action.upper())
    if email:
        query = query.filter(Audit.email.ilike(f"%{email}%"))
        
    return paginate(query.order_by(Audit.created_at.desc()), page, limit)
