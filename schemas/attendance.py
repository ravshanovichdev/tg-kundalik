"""
Pydantic schemas for Attendance model in SamIT Global system.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AttendanceBase(BaseModel):
    """Base attendance schema with common fields"""
    student_id: int = Field(..., description="Student ID")
    group_id: int = Field(..., description="Group ID")
    date: datetime = Field(..., description="Class date")
    status: str = Field(..., description="Attendance status: PRESENT, ABSENT, LATE")
    notes: Optional[str] = Field(None, description="Additional notes")


class AttendanceCreate(AttendanceBase):
    """Schema for creating new attendance record"""
    pass


class AttendanceUpdate(BaseModel):
    """Schema for updating attendance record"""
    status: Optional[str] = None
    notes: Optional[str] = None


class AttendanceResponse(AttendanceBase):
    """Schema for attendance response"""
    id: int
    marked_by: int  # User ID who marked attendance
    created_at: datetime
    updated_at: datetime
    status_display: Optional[str] = None  # Computed field

    class Config:
        orm_mode = True


class AttendanceWithStudent(AttendanceResponse):
    """Attendance response with student information"""
    student: Optional[dict] = None  # Student data


class AttendanceWithGroup(AttendanceResponse):
    """Attendance response with group information"""
    group: Optional[dict] = None  # Group data


class BulkAttendanceCreate(BaseModel):
    """Schema for bulk attendance creation"""
    group_id: int = Field(..., description="Group ID")
    date: datetime = Field(..., description="Class date")
    attendances: list[dict] = Field(..., description="List of {student_id: status} pairs")


class AttendanceStats(BaseModel):
    """Schema for attendance statistics"""
    total_classes: int
    present_count: int
    absent_count: int
    late_count: int
    attendance_percentage: float


class StudentAttendanceSummary(BaseModel):
    """Summary of student's attendance"""
    student_id: int
    total_classes: int
    present_count: int
    absent_count: int
    late_count: int
    attendance_percentage: float
    recent_attendance: list[AttendanceResponse] = []


class GroupAttendanceReport(BaseModel):
    """Attendance report for a group"""
    group_id: int
    group_name: str
    total_students: int
    date_range: dict  # {"start": date, "end": date}
    attendance_summary: AttendanceStats
    student_summaries: list[StudentAttendanceSummary] = []
