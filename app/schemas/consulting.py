import re
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from datetime import datetime

PERSONAL_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "icloud.com", "aol.com", "protonmail.com", "mail.com"
}


class OTPRequest(BaseModel):
    email: EmailStr


class OTPVerify(BaseModel):
    email: EmailStr
    otp: str


class ConsultingCreate(BaseModel):
    name: str
    email: EmailStr
    mobile_number: str
    company_name: str
    message: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_business_email(cls, v: str) -> str:
        domain = v.split("@")[-1].lower()
        if domain in PERSONAL_DOMAINS:
            raise ValueError("Please use a business email address")
        return v

    @field_validator("mobile_number")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("All integers should be used")
        if len(v) != 10:
            raise ValueError("Must be exactly 10 digits")
        return v


class ConsultingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    mobile_number: str
    company_name: str
    message: Optional[str]
    created_at: datetime
