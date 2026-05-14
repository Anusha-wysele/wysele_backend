from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.models.consulting import ConsultingInquiry
from app.models.user import User
from app.schemas.consulting import ConsultingCreate, ConsultingResponse
from app.schemas.pagination import PaginatedResponse, paginate

router = APIRouter()


# PUBLIC: Submit consulting inquiry
@router.post("/submit", response_model=ConsultingResponse)
def submit_consulting(body: ConsultingCreate, db: Session = Depends(deps.get_db)):
    count = db.query(ConsultingInquiry).filter(ConsultingInquiry.email == body.email).count()
    if count >= 10:
        raise HTTPException(status_code=400, detail="You have reached the maximum limit of 10 submissions")

    inquiry = ConsultingInquiry(
        name=body.name,
        email=body.email,
        mobile_number=body.mobile_number,
        company_name=body.company_name,
        message=body.message,
    )
    db.add(inquiry)
    db.commit()
    db.refresh(inquiry)
    return inquiry


# ADMIN with can_access_consulting permission
@router.get("/", response_model=PaginatedResponse[ConsultingResponse])
def get_all_consulting(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_can_access_consulting),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100)
):
    query = db.query(ConsultingInquiry).order_by(ConsultingInquiry.created_at.desc())
    return paginate(query, page, limit)


# ADMIN with can_access_consulting permission
@router.get("/{inquiry_id}", response_model=ConsultingResponse)
def get_consulting(
    inquiry_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_can_access_consulting)
):
    inquiry = db.query(ConsultingInquiry).filter(ConsultingInquiry.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="Consulting inquiry not found")
    return inquiry
