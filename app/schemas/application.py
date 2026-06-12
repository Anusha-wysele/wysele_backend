import re
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from typing import Optional
from datetime import datetime


class ApplicationCreate(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    mobileNumber: str
    currentLocation: str
    region: Optional[str] = None
    currentCtc: Optional[str] = None
    expectedCtc: Optional[str] = None
    noticePeriod: str
    releventExperience: str
    resume: str

    @field_validator("mobileNumber")
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


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    first_name: str
    last_name: str
    email: str
    mobile_number: str
    current_location: str
    region: Optional[str]
    current_ctc: Optional[str]
    expected_ctc: Optional[str]
    notice_period: str
    relevant_experience: str
    resume_url: str
    applied_at: datetime


class ApplicationSuccess(BaseModel):
    message: str = "Application submitted successfully"
    application: ApplicationResponse
