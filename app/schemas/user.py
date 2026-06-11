import re
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator, model_validator
from typing import Optional
from datetime import datetime

PERSONAL_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "icloud.com", "aol.com", "protonmail.com", "mail.com"
}

def validate_strong_password(value: str) -> str:
    if len(value) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not any(c.isupper() for c in value):
        raise ValueError("Password must contain at least one uppercase letter")
    if not any(c.islower() for c in value):
        raise ValueError("Password must contain at least one lowercase letter")
    if not any(c.isdigit() for c in value):
        raise ValueError("Password must contain at least one number")
    if not any(not c.isalnum() for c in value):
        raise ValueError("Password must contain at least one special character")
    return value


def validate_phone_number(v: Optional[str]) -> Optional[str]:
    if v is not None and v != "":
        if not v.isdigit():
            raise ValueError("All integers should be used")
        if len(v) != 10:
            raise ValueError("Must be exactly 10 digits")
    return v


class UserRegister(BaseModel):
    emp_id: str = Field(..., description="Unique Employee ID (e.g., WYT0015)")
    email: EmailStr
    name: str = Field(..., min_length=1)
    phone_number: Optional[str] = None
    company_name: str = Field(..., description="WYSELE, ORBINTIX, or GRACE VIRTUE")
    role: str = Field(..., description="SUPER_ADMIN or ADMIN")
    password: Optional[str] = None
    is_active: bool = True

    @field_validator("email")
    @classmethod
    def validate_business_email(cls, v: str) -> str:
        domain = v.split("@")[-1].lower()
        allowed_domains = {"wysele.com", "orbintix.com", "gracevirtue.com"}
        if domain not in allowed_domains:
            raise ValueError("Please use your official company email address")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ["SUPER_ADMIN", "ADMIN"]:
            raise ValueError("Role must be Admin or Super Admin")
        return v

    @field_validator("phone_number")
    @classmethod
    def validate_reg_phone(cls, v: Optional[str]) -> Optional[str]:
        return validate_phone_number(v)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validate_strong_password(v)
        return v

    @model_validator(mode="after")
    def validate_email_company_match(self) -> "UserRegister":
        email_domain = self.email.split("@")[-1].lower()
        company = self.company_name.upper().replace("_", " ")
        
        expected_companies = {
            "wysele.com": "WYSELE",
            "orbintix.com": "ORBINTIX",
            "gracevirtue.com": "GRACE VIRTUE"
        }
        
        expected_comp = expected_companies.get(email_domain)
        if expected_comp != company:
            raise ValueError("Email domain does not match the selected company")
            
        return self


class UserBase(BaseModel):
    emp_id: str
    email: EmailStr
    name: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    company_id: Optional[str] = None
    company_name: Optional[str] = None

    @field_validator("phone_number")
    @classmethod
    def validate_base_phone(cls, v: Optional[str]) -> Optional[str]:
        return validate_phone_number(v)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role: str = Field(..., description="Role must be SUPER_ADMIN or ADMIN")

    @field_validator("password")
    @classmethod
    def validate_create_password(cls, v: str) -> str:
        return validate_strong_password(v)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role: str
    is_active: bool
    is_first_login: bool
    can_post_blog: bool = False
    can_edit_blog: bool = False
    can_delete_blog: bool = False
    can_post_job: bool = False
    can_access_contact: bool = False
    can_access_consulting: bool = False
    created_at: datetime


class UserUpdate(BaseModel):
    name: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None
    emp_id: Optional[str] = None
    company_id: Optional[str] = None
    company_name: Optional[str] = None

    @field_validator("phone_number")
    @classmethod
    def validate_update_phone(cls, v: Optional[str]) -> Optional[str]:
        return validate_phone_number(v)


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
    token_type: str
    role: str
    is_first_login: bool
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_change_password(cls, v: str) -> str:
        return validate_strong_password(v)


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_reset_password(cls, v: str) -> str:
        return validate_strong_password(v)
