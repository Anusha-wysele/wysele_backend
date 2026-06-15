from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_super_admin
from app.models.company import Company
from app.models.user import User
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate

router = APIRouter()

@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(
    company_in: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    if company_in.id:
        comp_id = company_in.id.strip().lower()
    else:
        # Generate ID from company_name
        comp_id = company_in.company_name.strip().lower().replace(" ", "-")
        comp_id = "".join(c for c in comp_id if c.isalnum() or c in ("-", "_"))
        if not comp_id:
            comp_id = "company"

    # Check if company already exists
    existing = db.query(Company).filter(Company.id == comp_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Company ID already exists")

    new_company = Company(
        id=comp_id,
        company_name=company_in.company_name,
        company_type=company_in.company_type,
        company_email=company_in.company_email,
        description=company_in.description,
        website_url=company_in.website_url,
        company_representative=company_in.company_representative,
        documents=company_in.documents,
        address=company_in.address,
        is_active=company_in.is_active if company_in.is_active is not None else True
    )
    db.add(new_company)
    db.commit()
    db.refresh(new_company)
    return new_company

@router.get("/", response_model=List[CompanyResponse])
def list_companies(db: Session = Depends(get_db)):
    return db.query(Company).filter(Company.is_active == True).order_by(Company.company_name).all()

@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(company_id: str, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id.lower()).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: str,
    company_in: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    company = db.query(Company).filter(Company.id == company_id.lower()).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    update_data = company_in.model_dump(exclude_unset=True)
    
    # Prevent deactivating the last active company
    if "is_active" in update_data and update_data["is_active"] is False:
        if company.is_active:
            active_count = db.query(Company).filter(Company.is_active == True).count()
            if active_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="At least one company must remain active"
                )

    for field, value in update_data.items():
        setattr(company, field, value)

    db.commit()
    db.refresh(company)
    return company
