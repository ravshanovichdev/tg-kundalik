"""
Grade model for SamIT Global educational system.
Tracks student grades and assessments.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Grade(Base):
    """
    Grade model representing student grades.
    Types: exam, homework, test, quiz, etc.
    """
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    value = Column(Float, nullable=False)  # Оценка (5.0, 4.5, etc.)
    max_value = Column(Float, default=5.0)  # Максимальная оценка (обычно 5.0)
    type = Column(String(50), nullable=False)  # exam, homework, test, quiz, etc.
    title = Column(String(255), nullable=True)  # Название работы/теста
    description = Column(Text, nullable=True)  # Описание задания
    comment = Column(Text, nullable=True)  # Комментарий преподавателя
    date_given = Column(DateTime, nullable=False, index=True)  # Дата выставления оценки
    given_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Кто выставил (teacher user_id)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    student = relationship("Student", back_populates="grades")
    group = relationship("Group")
    teacher = relationship("User")

    @property
    def percentage(self):
        """Returns grade as percentage"""
        if self.max_value == 0:
            return 0
        return (self.value / self.max_value) * 100

    @property
    def grade_letter(self):
        """Returns letter grade based on percentage"""
        percentage = self.percentage
        if percentage >= 90:
            return "A"
        elif percentage >= 80:
            return "B"
        elif percentage >= 70:
            return "C"
        elif percentage >= 60:
            return "D"
        else:
            return "F"

    @property
    def type_display(self):
        """Human-readable grade type"""
        type_map = {
            "exam": "Экзамен",
            "homework": "Домашнее задание",
            "test": "Тест",
            "quiz": "Контрольная",
            "project": "Проект",
            "presentation": "Презентация"
        }
        return type_map.get(self.type, self.type)

    def __repr__(self):
        return f"<Grade(id={self.id}, student_id={self.student_id}, value={self.value}, type={self.type})>"
