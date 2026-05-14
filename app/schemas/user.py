import re
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime

PERSONAL_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "icloud.com", "aol.com", "protonmail.com", "mail.com"
}


class UserRegister(BaseModel):
    employee_id: str = Field(..., description="Unique Employee ID (e.g., WYT0015)")
    email: EmailStr
    first_name: str = Field(..., min_length=1)
    middle_name: Optional[str] = None
    last_name: str = Field(..., min_length=1)
    phone_number: Optional[str] = None
    company_id: Optional[str] = None
    role: str = Field(..., description="ADMIN or HR")

    @field_validator("email")
    @classmethod
    def validate_business_email(cls, v: str) -> str:
        domain = v.split("@")[-1].lower()
        if domain in PERSONAL_DOMAINS:
            raise ValueError("Please use a business email address")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ["ADMIN", "HR"]:
            raise ValueError("Role must be ADMIN or HR")
        return v


class UserBase(BaseModel):
    employee_id: str
    email: EmailStr
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    phone_number: Optional[str] = None
    company_id: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role: str = Field(..., description="Role must be ADMIN or HR")


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role: str
    is_active: bool
    is_first_login: bool
    can_post_blog: bool
    can_edit_blog: bool
    can_delete_blog: bool
    can_post_job: bool
    can_access_contact: bool
    can_access_consulting: bool
    created_at: datetime


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None
    employee_id: Optional[str] = None
    company_id: Optional[str] = None


class PermissionsUpdate(BaseModel):
    can_post_blog: Optional[bool] = None
    can_edit_blog: Optional[bool] = None
    can_delete_blog: Optional[bool] = None
    can_post_job: Optional[bool] = None
    can_access_contact: Optional[bool] = None
    can_access_consulting: Optional[bool] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    is_first_login: bool


class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
