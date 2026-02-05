"""
Group model for SamIT Global educational system.
Represents educational groups/classes managed by teachers.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Group(Base):
    """
    Group model representing educational classes/groups.
    Each group has a teacher and contains students.
    """
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)  # Название группы (например, "Математика 1А")
    subject = Column(String(255), nullable=False)  # Предмет
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    monthly_price = Column(Float, nullable=False, default=0.0)  # Месячная стоимость обучения
    schedule = Column(Text, nullable=True)  # Расписание занятий
    description = Column(Text, nullable=True)
    max_students = Column(Integer, default=30)  # Максимальное количество учеников
    is_active = Column(Integer, default=1)  # 1 - active, 0 - inactive
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    teacher = relationship("Teacher", back_populates="groups")
    students = relationship("Student", back_populates="group", cascade="all, delete-orphan")
    attendances = relationship("Attendance", back_populates="group", cascade="all, delete-orphan")

    @property
    def current_students_count(self):
        """Returns current number of active students in the group"""
        return len([s for s in self.students if s.is_active])

    @property
    def available_slots(self):
        """Returns number of available slots in the group"""
        return max(0, self.max_students - self.current_students_count)

    @property
    def is_full(self):
        """Check if group is at maximum capacity"""
        return self.current_students_count >= self.max_students

    @property
    def average_attendance(self):
        """Calculate average attendance percentage for the group"""
        if not self.students:
            return 0.0
        total_percentage = sum(student.attendance_percentage for student in self.students if student.is_active)
        active_students = len([s for s in self.students if s.is_active])
        return total_percentage / active_students if active_students > 0 else 0.0

    def __repr__(self):
        return f"<Group(id={self.id}, name={self.name}, teacher_id={self.teacher_id}, students={self.current_students_count})>"
