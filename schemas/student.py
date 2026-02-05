"""
Pydantic schemas for Student model in SamIT Global system.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class StudentBase(BaseModel):
    """Base student schema with common fields"""
    first_name: str = Field(..., description="Student's first name")
    last_name: str = Field(..., description="Student's last name")
    date_of_birth: Optional[datetime] = Field(None, description="Date of birth")
    parent_id: int = Field(..., description="Parent user ID")
    group_id: int = Field(..., description="Group ID")
    phone: Optional[str] = Field(None, description="Contact phone")
    address: Optional[str] = Field(None, description="Home address")
    notes: Optional[str] = Field(None, description="Additional notes")


class StudentCreate(StudentBase):
    """Schema for creating new student"""
    pass


class StudentUpdate(BaseModel):
    """Schema for updating student"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    group_id: Optional[int] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[int] = None


class StudentResponse(StudentBase):
    """Schema for student response"""
    id: int
    is_active: int
    created_at: datetime
    updated_at: datetime
    full_name: Optional[str] = None  # Computed field
    average_grade: Optional[float] = None  # Computed field
    attendance_percentage: Optional[float] = None  # Computed field

    class Config:
        from_attributes = True


class StudentWithParent(StudentResponse):
    """Student response with parent information"""
    parent: Optional[dict] = None  # Parent user data


class StudentWithGroup(StudentResponse):
    """Student response with group information"""
    group: Optional[dict] = None  # Group data


class StudentStats(BaseModel):
    """Schema for student statistics"""
    total_students: int
    active_students: int
    inactive_students: int
    average_age: Optional[float] = None
    average_attendance: Optional[float] = None
