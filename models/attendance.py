"""
Attendance model for SamIT Global educational system.
Tracks student attendance records.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Attendance(Base):
    """
    Attendance model representing student attendance records.
    Status: PRESENT, ABSENT, LATE
    """
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    date = Column(DateTime, nullable=False, index=True)  # Дата занятия
    status = Column(String(20), nullable=False)  # PRESENT, ABSENT, LATE
    notes = Column(Text, nullable=True)  # Примечания (опоздание на 15 мин и т.д.)
    marked_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Кто отметил (teacher user_id)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    student = relationship("Student", back_populates="attendances")
    group = relationship("Group", back_populates="attendances")
    marker = relationship("User")

    @property
    def is_present(self):
        """Check if student was present"""
        return self.status == "PRESENT"

    @property
    def is_absent(self):
        """Check if student was absent"""
        return self.status == "ABSENT"

    @property
    def is_late(self):
        """Check if student was late"""
        return self.status == "LATE"

    @property
    def status_display(self):
        """Human-readable status"""
        status_map = {
            "PRESENT": "Присутствовал",
            "ABSENT": "Отсутствовал",
            "LATE": "Опоздал"
        }
        return status_map.get(self.status, self.status)

    def __repr__(self):
        return f"<Attendance(id={self.id}, student_id={self.student_id}, date={self.date}, status={self.status})>"
