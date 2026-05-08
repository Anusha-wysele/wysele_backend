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
        if not re.fullmatch(r"\d{10}", v):
            raise ValueError("mobileNumber must be exactly 10 digits")
        return v


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
