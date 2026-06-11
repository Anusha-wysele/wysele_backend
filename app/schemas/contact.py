from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from typing import Optional
from datetime import datetime

class ContactCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone_number: Optional[str] = None
    location: Optional[str] = None
    message: str

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v != "":
            if not v.isdigit():
                raise ValueError("All integers should be used")
            if len(v) != 10:
                raise ValueError("Must be exactly 10 digits")
        return v

class ContactResponse(ContactCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
