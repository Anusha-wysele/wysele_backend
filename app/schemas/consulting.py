import re
from typing import Optional
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
    message: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_business_email(cls, v: str) -> str:
        domain = v.split("@")[-1].lower()
        allowed = {"wysele.com", "orbintix.com", "gracevirtue.com"}
        if domain not in allowed:
            raise ValueError("Please use a business email address")
        return v

    @field_validator("mobile_number")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        # Strip common formatting characters: spaces, hyphens, parentheses, plus signs
        cleaned = re.sub(r"[\s\-\(\)\+]", "", v)
        # Handle country code (+91 or 91) prefix for 12 digit numbers
        if cleaned.startswith("91") and len(cleaned) == 12:
            cleaned = cleaned[2:]
        # Handle leading zero prefix for 11 digit numbers
        elif cleaned.startswith("0") and len(cleaned) == 11:
            cleaned = cleaned[1:]

        if not cleaned.isdigit():
            raise ValueError("All integers should be used")
        if len(cleaned) != 10:
            raise ValueError("Must be exactly 10 digits")
        return cleaned


class ConsultingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    mobile_number: str
    company_name: str
    message: Optional[str]
    created_at: datetime
