"""
Pydantic schemas for Schedule model in SamIT Global system.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, time


class ScheduleBase(BaseModel):
    """Base schedule schema with common fields"""
    group_id: int = Field(..., description="Group ID")
    day_of_week: int = Field(..., ge=0, le=6, description="Day of week (0=Sunday, 6=Saturday)")
    start_time: time = Field(..., description="Start time")
    end_time: time = Field(..., description="End time")
    subject: str = Field(..., description="Subject name")
    teacher_id: int = Field(..., description="Teacher ID")
    room: Optional[str] = Field(None, description="Room number")


class ScheduleCreate(ScheduleBase):
    """Schema for creating new schedule"""
    pass


class ScheduleUpdate(BaseModel):
    """Schema for updating schedule"""
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    subject: Optional[str] = None
    teacher_id: Optional[int] = None
    room: Optional[str] = None


class ScheduleResponse(ScheduleBase):
    """Schema for schedule response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

