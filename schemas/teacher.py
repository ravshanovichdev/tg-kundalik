"""
Pydantic schemas for Teacher model in SamIT Global system.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class TeacherBase(BaseModel):
    """Base teacher schema with common fields"""
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    phone: Optional[str] = Field(None, description="Phone number")
    email: Optional[EmailStr] = Field(None, description="Email address")
    specialization: Optional[str] = Field(None, description="Subject specialization")
    experience_years: int = Field(0, description="Years of experience")
    bio: Optional[str] = Field(None, description="Biography")


class TeacherCreate(TeacherBase):
    """Schema for creating new teacher"""
    user_id: int = Field(..., description="Associated user ID")
    telegram_id: Optional[int] = Field(None, description="Telegram ID (if creating user too)")


class TeacherUpdate(BaseModel):
    """Schema for updating teacher"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    specialization: Optional[str] = None
    experience_years: Optional[int] = None
    bio: Optional[str] = None
    is_active: Optional[int] = None


class TeacherResponse(TeacherBase):
    """Schema for teacher response"""
    id: int
    user_id: int
    is_active: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

