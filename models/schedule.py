"""
Schedule model for SamIT Global educational system.
Represents class schedules for groups.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Schedule(Base):
    """
    Schedule model representing class schedules.
    Each schedule entry represents a lesson time for a group.
    """
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0-6 (Sunday-Saturday)
    start_time = Column(Time, nullable=False)  # Время начала занятия
    end_time = Column(Time, nullable=False)  # Время окончания занятия
    subject = Column(String(255), nullable=False)  # Предмет (может отличаться от группы)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    room = Column(String(50), nullable=True)  # Кабинет
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    group = relationship("Group")
    teacher = relationship("Teacher")

    @property
    def day_name(self):
        """Returns day name in Russian"""
        days = ["Воскресенье", "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
        if 0 <= self.day_of_week <= 6:
            return days[self.day_of_week]
        return f"День {self.day_of_week}"

    def __repr__(self):
        return f"<Schedule(id={self.id}, group_id={self.group_id}, day={self.day_of_week}, time={self.start_time}-{self.end_time})>"

