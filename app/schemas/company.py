from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CompanyBase(BaseModel):
    name: str = Field(..., min_length=1)
    domain: str = Field(..., min_length=1)
    email_domain: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    domain_link: str = Field(..., min_length=1)
    responsible_person: str = Field(..., min_length=1)
    documents: Optional[str] = None
    address: str = Field(..., min_length=1)
    is_active: Optional[bool] = True

class CompanyCreate(CompanyBase):
    id: str = Field(..., min_length=1, pattern="^[a-z0-9_-]+$", description="Lowercase unique identifier, e.g. 'wysele'")

class CompanyUpdate(BaseModel):
    name: str = Field(default=None, min_length=1)
    domain: str = Field(default=None, min_length=1)
    email_domain: str = Field(default=None, min_length=1)
    description: str = Field(default=None, min_length=1)
    domain_link: str = Field(default=None, min_length=1)
    responsible_person: str = Field(default=None, min_length=1)
    documents: Optional[str] = None
    address: str = Field(default=None, min_length=1)
    is_active: bool = Field(default=None)

class CompanyResponse(CompanyBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
