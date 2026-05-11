import re
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from datetime import datetime


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
    department: str
    message: str

    @field_validator("mobile_number")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        if not re.fullmatch(r"\d{10}", v):
            raise ValueError("mobile_number must be exactly 10 digits")
        return v


class ConsultingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    mobile_number: str
    company_name: str
    department: str
    message: str
    created_at: datetime
