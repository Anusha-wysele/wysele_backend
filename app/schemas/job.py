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
    openings: int = Field(..., ge=1)
    location: str
    min_salary: int
    max_salary: int
    description: str
    responsibilities: List[str] = Field(..., min_length=1)
    required_skills: List[str] = Field(..., min_length=1)
    qualification: str
    application_email: str
    application_deadline: date
    role: str
    company_id: str
    status: str = "ACTIVE"

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v_upper = v.upper()
            if v_upper not in ["ACTIVE", "DRAFT", "CLOSED"]:
                raise ValueError("Status must be ACTIVE, DRAFT, or CLOSED")
            return v_upper
        return v

    @field_validator(
        "job_code", "company_name", "job_title", "department", "employment_type", 
        "work_mode", "experience", "location", "description", "qualification", 
        "application_email", "role", "company_id", "status", mode="before"
    )
    @classmethod
    def check_not_empty_string(cls, v):
        if isinstance(v, str):
            stripped = v.strip()
            if not stripped:
                raise ValueError("Field cannot be empty or only whitespace")
            return stripped
        return v

    @field_validator("responsibilities", "required_skills", mode="before")
    @classmethod
    def check_non_empty_list_elements(cls, v):
        if isinstance(v, list):
            cleaned = []
            for item in v:
                if isinstance(item, str):
                    stripped = item.strip()
                    if not stripped:
                        raise ValueError("List elements cannot be empty or only whitespace")
                    cleaned.append(stripped)
                else:
                    cleaned.append(item)
            return cleaned
        return v


class JobUpdate(BaseModel):
    company_name: str
    job_title: str
    department: str
    employment_type: str
    work_mode: str
    experience: str
    openings: int = Field(..., ge=1)
    location: str
    min_salary: int
    max_salary: int
    description: str
    responsibilities: List[str] = Field(..., min_length=1)
    required_skills: List[str] = Field(..., min_length=1)
    qualification: str
    application_email: str
    application_deadline: date
    role: str
    company_id: str
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v_upper = v.upper()
            if v_upper not in ["ACTIVE", "DRAFT", "CLOSED"]:
                raise ValueError("Status must be ACTIVE, DRAFT, or CLOSED")
            return v_upper
        return v

    @field_validator(
        "company_name", "job_title", "department", "employment_type", 
        "work_mode", "experience", "location", "description", "qualification", 
        "application_email", "role", "company_id", "status", mode="before"
    )
    @classmethod
    def check_not_empty_string(cls, v):
        if isinstance(v, str):
            stripped = v.strip()
            if not stripped:
                raise ValueError("Field cannot be empty or only whitespace")
            return stripped
        return v

    @field_validator("responsibilities", "required_skills", mode="before")
    @classmethod
    def check_non_empty_list_elements(cls, v):
        if isinstance(v, list):
            cleaned = []
            for item in v:
                if isinstance(item, str):
                    stripped = item.strip()
                    if not stripped:
                        raise ValueError("List elements cannot be empty or only whitespace")
                    cleaned.append(stripped)
                else:
                    cleaned.append(item)
            return cleaned
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
