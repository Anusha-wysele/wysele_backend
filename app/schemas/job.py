from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import date, datetime


class JobCreate(BaseModel):
    description: str
    experience: str
    jobCode: str
    jobPostedDate: date
    jobType: str
    keySkills: List[str] = Field(..., min_length=1)
    responsibilities: Optional[List[str]] = None
    lastDateToApply: date
    location: str
    region: str
    role: str
    salary: Optional[str] = None
    company_id: Optional[str] = None
    company_name: Optional[str] = None


class JobUpdate(BaseModel):
    description: Optional[str] = None
    experience: Optional[str] = None
    jobType: Optional[str] = None
    keySkills: Optional[List[str]] = None
    responsibilities: Optional[List[str]] = None
    lastDateToApply: Optional[date] = None
    location: Optional[str] = None
    region: Optional[str] = None
    role: Optional[str] = None
    salary: Optional[str] = None
    company_id: Optional[str] = None
    company_name: Optional[str] = None


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str
    experience: str
    job_code: str
    job_posted_date: date
    job_type: str
    key_skills: List[str]
    responsibilities: Optional[List[str]]
    last_date_to_apply: date
    location: str
    region: str
    role: str
    salary: Optional[str]
    status: str
    posted_by: int
    company_id: Optional[str]
    company_name: Optional[str]
    created_at: datetime
