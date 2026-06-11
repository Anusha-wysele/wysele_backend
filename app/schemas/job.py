from pydantic import BaseModel, ConfigDict, Field
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
    status: Optional[str] = "Active"


class JobUpdate(BaseModel):
    job_title: Optional[str] = None
    department: Optional[str] = None
    employment_type: Optional[str] = None
    work_mode: Optional[str] = None
    experience: Optional[str] = None
    openings: Optional[int] = None
    location: Optional[str] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    description: Optional[str] = None
    responsibilities: Optional[List[str]] = None
    required_skills: Optional[List[str]] = None
    qualification: Optional[str] = None
    application_email: Optional[str] = None
    application_deadline: Optional[date] = None
    role: Optional[str] = None
    company_id: Optional[str] = None
    company_name: Optional[str] = None
    status: Optional[str] = None


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
