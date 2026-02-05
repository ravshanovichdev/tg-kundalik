"""
Student model for SamIT Global educational system.
Represents students enrolled in educational groups.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Student(Base):
    """
    Student model representing enrolled students.
    Each student belongs to a parent and a group.
    """
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    date_of_birth = Column(DateTime, nullable=True)
    parent_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Integer, default=1)  # 1 - active, 0 - inactive
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    parent = relationship("User", back_populates="children")
    group = relationship("Group", back_populates="students")
    attendances = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")
    grades = relationship("Grade", back_populates="student", cascade="all, delete-orphan")

    @property
    def full_name(self):
        """Returns student's full name"""
        return f"{self.first_name} {self.last_name}"

    @property
    def average_grade(self):
        """Calculate average grade from all grades"""
        if not self.grades:
            return 0.0
        return sum(grade.value for grade in self.grades) / len(self.grades)

    @property
    def attendance_percentage(self):
        """Calculate attendance percentage"""
        if not self.attendances:
            return 0.0
        present_count = sum(1 for att in self.attendances if att.status == "PRESENT")
        return (present_count / len(self.attendances)) * 100

    def __repr__(self):
        return f"<Student(id={self.id}, name={self.full_name}, group_id={self.group_id})>"
