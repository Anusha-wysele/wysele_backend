import random
import string
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.models.consulting import ConsultingInquiry
from app.models.email_verification import EmailVerification
from app.schemas.consulting import OTPRequest, OTPVerify, ConsultingCreate, ConsultingResponse
from app.schemas.pagination import PaginatedResponse, paginate
from app.services.email_service import send_otp_email

router = APIRouter()

PURPOSE = "consulting"


def _generate_otp() -> str:
    return "".join(random.choices(string.digits, k=6))


# GET /consulting — All submissions (paginated)
@router.get("/", response_model=PaginatedResponse[ConsultingResponse])
def get_all_consulting(
    db: Session = Depends(deps.get_db),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100)
):
    query = db.query(ConsultingInquiry).order_by(ConsultingInquiry.created_at.desc())
    return paginate(query, page, limit)


# GET /consulting/{id} — Single submission
@router.get("/{inquiry_id}", response_model=ConsultingResponse)
def get_consulting(inquiry_id: int, db: Session = Depends(deps.get_db)):
    inquiry = db.query(ConsultingInquiry).filter(ConsultingInquiry.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="Consulting inquiry not found")
    return inquiry


# STEP 1: Send OTP
@router.post("/send-otp")
def send_otp(body: OTPRequest, background_tasks: BackgroundTasks, db: Session = Depends(deps.get_db)):
    otp = _generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    db.query(EmailVerification).filter(
        EmailVerification.email == body.email,
        EmailVerification.purpose == PURPOSE,
        EmailVerification.is_verified == False
    ).delete()
    db.commit()

    db.add(EmailVerification(email=body.email, otp=otp, purpose=PURPOSE, is_verified=False, expires_at=expires_at))
    db.commit()

    background_tasks.add_task(send_otp_email, email_to=body.email, otp=otp, purpose=PURPOSE)
    return {"message": "OTP sent to your email. It expires in 10 minutes."}


# STEP 2: Verify OTP
@router.post("/verify-otp")
def verify_otp(body: OTPVerify, db: Session = Depends(deps.get_db)):
    record = db.query(EmailVerification).filter(
        EmailVerification.email == body.email,
        EmailVerification.purpose == PURPOSE,
        EmailVerification.is_verified == False,
    ).order_by(EmailVerification.created_at.desc()).first()

    if not record:
        raise HTTPException(status_code=400, detail="No pending OTP found for this email")
    if datetime.now(timezone.utc) > record.expires_at:
        raise HTTPException(status_code=400, detail="OTP has expired. Please request a new one")
    if record.otp != body.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    record.is_verified = True
    db.commit()
    return {"message": "Email verified successfully."}


# STEP 3: Submit form
@router.post("/submit", response_model=ConsultingResponse)
def submit_consulting(body: ConsultingCreate, db: Session = Depends(deps.get_db)):
    verified = db.query(EmailVerification).filter(
        EmailVerification.email == body.email,
        EmailVerification.purpose == PURPOSE,
        EmailVerification.is_verified == True,
    ).order_by(EmailVerification.created_at.desc()).first()

    if not verified:
        raise HTTPException(status_code=403, detail="Email not verified. Please verify your email first")

    inquiry = ConsultingInquiry(
        name=body.name,
        email=body.email,
        mobile_number=body.mobile_number,
        company_name=body.company_name,
        department=body.department,
        message=body.message,
    )
    db.add(inquiry)
    db.delete(verified)
    db.commit()
    db.refresh(inquiry)
    return inquiry
