"""
User model for SamIT Global educational system.
Represents users with different roles: admin, teacher, parent.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """
    User model representing all system users.
    Roles: admin, teacher, parent
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=True)
    role = Column(String(20), nullable=False, default="parent")  # admin, teacher, parent
    is_active = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    teacher_profile = relationship("Teacher", back_populates="user", uselist=False, cascade="all, delete-orphan")
    children = relationship("Student", back_populates="parent", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, role={self.role}, full_name={self.full_name})>"

    @property
    def is_admin(self) -> bool:
        """Check if user has admin role"""
        return self.role == "admin"

    @property
    def is_teacher(self) -> bool:
        """Check if user has teacher role"""
        return self.role == "teacher"

    @property
    def is_parent(self) -> bool:
        """Check if user has parent role"""
        return self.role == "parent"
