from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, List
from datetime import date, datetime


class JobCreate(BaseModel):
    job_code: str
    company_name: str
    job_title: str
    department: str
    employment_type: str
    work_mode: str
    experience: str
    openings: int
    location: str
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    description: str
    responsibilities: Optional[List[str]] = None
    required_skills: List[str] = Field(..., min_length=1)
    qualification: Optional[str] = None
    application_email: Optional[str] = None
    application_deadline: date
    role: str
    company_id: Optional[str] = None
    status: Optional[str] = "ACTIVE"

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v_upper = v.upper()
            if v_upper not in ["ACTIVE", "DRAFT", "CLOSED"]:
                raise ValueError("Status must be ACTIVE, DRAFT, or CLOSED")
            return v_upper
        return v


class JobUpdate(BaseModel):
    job_title: str = Field(default=None, min_length=1)
    department: str = Field(default=None, min_length=1)
    employment_type: str = Field(default=None, min_length=1)
    work_mode: str = Field(default=None, min_length=1)
    experience: str = Field(default=None, min_length=1)
    openings: int = Field(default=None, ge=1)
    location: str = Field(default=None, min_length=1)
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    description: str = Field(default=None, min_length=1)
    responsibilities: Optional[List[str]] = None
    required_skills: List[str] = Field(default=None, min_length=1)
    qualification: Optional[str] = None
    application_email: Optional[str] = None
    application_deadline: date = Field(default=None)
    role: str = Field(default=None, min_length=1)
    company_id: Optional[str] = None
    company_name: str = Field(default=None, min_length=1)
    status: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v_upper = v.upper()
            if v_upper not in ["ACTIVE", "DRAFT", "CLOSED"]:
                raise ValueError("Status must be ACTIVE, DRAFT, or CLOSED")
            return v_upper
        return v


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_code: str
    company_name: str
    job_title: str
    department: str
    employment_type: str
    work_mode: str
    experience: str
    openings: int
    location: str
    min_salary: Optional[int]
    max_salary: Optional[int]
    description: str
    responsibilities: Optional[List[str]]
    required_skills: List[str]
    qualification: Optional[str]
    application_email: Optional[str]
    application_deadline: date
    status: str
    posted_by: int
    company_id: Optional[str]
    created_at: datetime


class JobCreateSuccess(BaseModel):
    message: str = "Job posted successfully"
    job: JobResponse
