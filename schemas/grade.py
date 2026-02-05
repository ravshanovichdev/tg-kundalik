"""
Pydantic schemas for Grade model in SamIT Global system.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class GradeBase(BaseModel):
    """Base grade schema with common fields"""
    student_id: int = Field(..., description="Student ID")
    group_id: int = Field(..., description="Group ID")
    value: float = Field(..., description="Grade value (e.g., 5.0, 4.5)")
    max_value: float = Field(5.0, description="Maximum possible grade")
    type: str = Field(..., description="Grade type: exam, homework, test, quiz, etc.")
    title: Optional[str] = Field(None, description="Title of the assignment/test")
    description: Optional[str] = Field(None, description="Assignment description")
    comment: Optional[str] = Field(None, description="Teacher's comment")
    date_given: datetime = Field(..., description="Date when grade was given")


class GradeCreate(GradeBase):
    """Schema for creating new grade"""
    pass


class GradeUpdate(BaseModel):
    """Schema for updating grade"""
    value: Optional[float] = None
    max_value: Optional[float] = None
    type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    comment: Optional[str] = None
    date_given: Optional[datetime] = None


class GradeResponse(GradeBase):
    """Schema for grade response"""
    id: int
    given_by: int  # Teacher user ID
    created_at: datetime
    updated_at: datetime
    percentage: Optional[float] = None  # Computed field
    grade_letter: Optional[str] = None  # Computed field
    type_display: Optional[str] = None  # Computed field

    class Config:
        from_attributes = True


class GradeWithStudent(GradeResponse):
    """Grade response with student information"""
    student: Optional[dict] = None  # Student data


class GradeWithTeacher(GradeResponse):
    """Grade response with teacher information"""
    teacher: Optional[dict] = None  # Teacher data


class GradeStats(BaseModel):
    """Schema for grade statistics"""
    total_grades: int
    average_grade: float
    highest_grade: float
    lowest_grade: float
    grade_distribution: dict  # e.g., {"A": 10, "B": 15, "C": 8, ...}


class StudentGradesSummary(BaseModel):
    """Summary of student's grades"""
    student_id: int
    total_grades: int
    average_grade: float
    recent_grades: list[GradeResponse] = []
