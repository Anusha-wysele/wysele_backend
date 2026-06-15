from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CompanyBase(BaseModel):
    company_name: str = Field(..., min_length=1)
    company_type: str = Field(..., min_length=1)
    company_email: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    website_url: str = Field(..., min_length=1)
    company_representative: str = Field(..., min_length=1)
    documents: Optional[str] = None
    address: str = Field(..., min_length=1)
    is_active: Optional[bool] = True

class CompanyCreate(CompanyBase):
    id: Optional[str] = Field(None, pattern="^[a-z0-9_-]+$", description="Optional lowercase unique identifier, e.g. 'wysele'")

class CompanyUpdate(BaseModel):
    company_name: Optional[str] = Field(default=None, min_length=1)
    company_type: Optional[str] = Field(default=None, min_length=1)
    company_email: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = Field(default=None, min_length=1)
    website_url: Optional[str] = Field(default=None, min_length=1)
    company_representative: Optional[str] = Field(default=None, min_length=1)
    documents: Optional[str] = None
    address: Optional[str] = Field(default=None, min_length=1)
    is_active: Optional[bool] = Field(default=None)

class CompanyResponse(CompanyBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
