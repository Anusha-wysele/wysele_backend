from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api import deps
from app.models.contact import ContactInquiry
from app.models.user import User
from app.schemas.contact import ContactCreate, ContactResponse
from app.schemas.pagination import PaginatedResponse, paginate

router = APIRouter()


# PUBLIC: Submit contact inquiry
@router.post("/", response_model=ContactResponse)
def submit_inquiry(contact_in: ContactCreate, db: Session = Depends(deps.get_db)):
    new_inquiry = ContactInquiry(**contact_in.model_dump())
    db.add(new_inquiry)
    db.commit()
    db.refresh(new_inquiry)
    return new_inquiry


# ADMIN with can_access_contact permission
@router.get("/all", response_model=PaginatedResponse[ContactResponse])
def get_all_inquiries(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_can_access_contact),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100)
):
    query = db.query(ContactInquiry).order_by(ContactInquiry.created_at.desc())
    return paginate(query, page, limit)


# ADMIN with can_access_contact permission
@router.delete("/{inquiry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inquiry(
    inquiry_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_can_access_contact)
):
    inquiry = db.query(ContactInquiry).filter(ContactInquiry.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    db.delete(inquiry)
    db.commit()
