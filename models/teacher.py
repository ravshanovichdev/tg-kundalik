"""
Teacher model for SamIT Global educational system.
Represents teachers who manage groups and students.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Teacher(Base):
    """
    Teacher model representing teaching staff.
    Each teacher is linked to a user account and manages groups.
    """
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    specialization = Column(String(255), nullable=True)  # Предмет специализации
    experience_years = Column(Integer, default=0)
    bio = Column(Text, nullable=True)
    is_active = Column(Integer, default=1)  # 1 - active, 0 - inactive
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="teacher_profile")
    groups = relationship("Group", back_populates="teacher", cascade="all, delete-orphan")

    @property
    def full_name(self):
        """Returns teacher's full name"""
        return f"{self.first_name} {self.last_name}"

    @property
    def active_groups_count(self):
        """Returns count of active groups"""
        return len([group for group in self.groups if group.is_active])

    @property
    def total_students(self):
        """Returns total number of students across all groups"""
        return sum(len(group.students) for group in self.groups if group.is_active)

    def __repr__(self):
        return f"<Teacher(id={self.id}, name={self.full_name}, user_id={self.user_id})>"
