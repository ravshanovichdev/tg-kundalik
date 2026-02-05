"""
Payment model for SamIT Global educational system.
Tracks student payment records and statuses.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Payment(Base):
    """
    Payment model representing student payment records.
    Status: PAID, UNPAID, OVERDUE
    """
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    amount = Column(Float, nullable=False)  # Сумма платежа
    currency = Column(String(10), default="UZS")  # Валюта
    month = Column(Integer, nullable=False)  # Месяц (1-12)
    year = Column(Integer, nullable=False)  # Год
    status = Column(String(20), nullable=False, default="UNPAID")  # PAID, UNPAID, OVERDUE
    payment_date = Column(DateTime, nullable=True)  # Дата оплаты
    due_date = Column(DateTime, nullable=True)  # Срок оплаты
    notes = Column(Text, nullable=True)  # Примечания
    processed_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Кто обработал платеж
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    student = relationship("Student")
    group = relationship("Group")
    processor = relationship("User")

    @property
    def is_paid(self):
        """Check if payment is completed"""
        return self.status == "PAID"

    @property
    def is_unpaid(self):
        """Check if payment is pending"""
        return self.status == "UNPAID"

    @property
    def is_overdue(self):
        """Check if payment is overdue"""
        return self.status == "OVERDUE"

    @property
    def month_year_display(self):
        """Human-readable month and year"""
        months = [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]
        if 1 <= self.month <= 12:
            return f"{months[self.month - 1]} {self.year}"
        return f"Месяц {self.month} {self.year}"

    @property
    def status_display(self):
        """Human-readable payment status"""
        status_map = {
            "PAID": "Оплачено",
            "UNPAID": "Не оплачено",
            "OVERDUE": "Просрочено"
        }
        return status_map.get(self.status, self.status)

    def __repr__(self):
        return f"<Payment(id={self.id}, student_id={self.student_id}, amount={self.amount}, status={self.status}, month={self.month}, year={self.year})>"
