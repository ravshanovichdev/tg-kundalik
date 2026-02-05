"""
Pydantic schemas for User model in SamIT Global system.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema with common fields"""
    telegram_id: int = Field(..., description="Telegram user ID")
    username: Optional[str] = Field(None, description="Telegram username")
    full_name: Optional[str] = Field(None, description="Full name")
    role: str = Field("parent", description="User role: admin, teacher, parent")


class UserCreate(UserBase):
    """Schema for creating new user"""
    pass


class UserUpdate(BaseModel):
    """Schema for updating user"""
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    is_blocked: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    is_active: bool
    is_blocked: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserStats(BaseModel):
    """Schema for user statistics"""
    total_users: int
    active_users: int
    blocked_users: int
    admins_count: int
    teachers_count: int
    parents_count: int


class CurrentUser(UserResponse):
    """Schema for current authenticated user"""
    pass
