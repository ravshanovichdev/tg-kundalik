"""
Payment service for SamIT Global system.
Handles payment processing, status updates, and overdue payment management.
"""
import logging
from datetime import datetime, date
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from models.payment import Payment
from models.student import Student
from models.group import Group
from services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class PaymentService:
    """
    Service for managing student payments.
    Handles payment creation, status updates, and notifications.
    """

    @staticmethod
    def create_payment_for_student(
        db: Session,
        student_id: int,
        month: int,
        year: int,
        amount: Optional[float] = None
    ) -> Optional[Payment]:
        """
        Create payment record for student.
        Uses group price if amount not specified.

        Args:
            db: Database session
            student_id: Student ID
            month: Payment month (1-12)
            year: Payment year
            amount: Payment amount (optional)

        Returns:
            Payment: Created payment record or None if error
        """
        try:
            # Get student and group info
            student = db.query(Student).filter(Student.id == student_id).first()
            if not student:
                logger.error(f"Student {student_id} not found")
                return None

            group = db.query(Group).filter(Group.id == student.group_id).first()
            if not group:
                logger.error(f"Group for student {student_id} not found")
                return None

            # Use group price if amount not provided
            if amount is None:
                amount = group.monthly_price

            # Check if payment already exists
            existing_payment = db.query(Payment).filter(
                and_(
                    Payment.student_id == student_id,
                    Payment.month == month,
                    Payment.year == year
                )
            ).first()

            if existing_payment:
                logger.info(f"Payment already exists for student {student_id}, month {month}/{year}")
                return existing_payment

            # Create payment record
            payment = Payment(
                student_id=student_id,
                group_id=student.group_id,
                amount=amount,
                month=month,
                year=year,
                status="UNPAID"
            )

            db.add(payment)
            db.commit()
            db.refresh(payment)

            logger.info(f"Created payment record for student {student_id}, amount {amount}")
            return payment

        except Exception as e:
            logger.error(f"Error creating payment for student {student_id}: {e}")
            db.rollback()
            return None

    @staticmethod
    def mark_payment_paid(
        db: Session,
        payment_id: int,
        payment_date: Optional[datetime] = None,
        processed_by: Optional[int] = None
    ) -> bool:
        """
        Mark payment as paid.

        Args:
            db: Database session
            payment_id: Payment ID
            payment_date: Payment date (optional, defaults to now)
            processed_by: User ID who processed payment

        Returns:
            bool: Success status
        """
        try:
            payment = db.query(Payment).filter(Payment.id == payment_id).first()
            if not payment:
                logger.error(f"Payment {payment_id} not found")
                return False

            payment.status = "PAID"
            payment.payment_date = payment_date or datetime.utcnow()
            if processed_by:
                payment.processed_by = processed_by

            db.commit()

            logger.info(f"Marked payment {payment_id} as paid")
            return True

        except Exception as e:
            logger.error(f"Error marking payment {payment_id} as paid: {e}")
            db.rollback()
            return False

    @staticmethod
    def mark_payment_unpaid(
        db: Session,
        payment_id: int,
        processed_by: Optional[int] = None
    ) -> bool:
        """
        Mark payment as unpaid and send reminder.

        Args:
            db: Database session
            payment_id: Payment ID
            processed_by: User ID who processed payment

        Returns:
            bool: Success status
        """
        try:
            payment = db.query(Payment).filter(Payment.id == payment_id).first()
            if not payment:
                logger.error(f"Payment {payment_id} not found")
                return False

            payment.status = "UNPAID"
            payment.payment_date = None
            if processed_by:
                payment.processed_by = processed_by

            db.commit()

            # Send payment reminder notification
            await NotificationService.send_payment_reminder(
                db, payment.student_id, payment.month, payment.year
            )

            logger.info(f"Marked payment {payment_id} as unpaid and sent reminder")
            return True

        except Exception as e:
            logger.error(f"Error marking payment {payment_id} as unpaid: {e}")
            db.rollback()
            return False

    @staticmethod
    def get_overdue_payments(
        db: Session,
        days_overdue: int = 30
    ) -> List[Payment]:
        """
        Get payments that are overdue.

        Args:
            db: Database session
            days_overdue: Days past due date to consider overdue

        Returns:
            List[Payment]: List of overdue payments
        """
        try:
            # For now, consider payments unpaid for more than specified days as overdue
            # In production, you'd have a proper due_date field

            cutoff_date = datetime.utcnow() - timedelta(days=days_overdue)

            overdue_payments = db.query(Payment).filter(
                and_(
                    Payment.status == "UNPAID",
                    Payment.created_at < cutoff_date
                )
            ).all()

            return overdue_payments

        except Exception as e:
            logger.error(f"Error getting overdue payments: {e}")
            return []

    @staticmethod
    def generate_monthly_payments(
        db: Session,
        month: int,
        year: int
    ) -> Dict[str, int]:
        """
        Generate payment records for all active students for given month.

        Args:
            db: Database session
            month: Month (1-12)
            year: Year

        Returns:
            Dict[str, int]: Statistics about created payments
        """
        try:
            created_count = 0
            skipped_count = 0

            # Get all active students
            active_students = db.query(Student).filter(Student.is_active == 1).all()

            for student in active_students:
                payment = PaymentService.create_payment_for_student(
                    db, student.id, month, year
                )
                if payment:
                    created_count += 1
                else:
                    skipped_count += 1

            logger.info(f"Generated monthly payments: created {created_count}, skipped {skipped_count}")

            return {
                "created": created_count,
                "skipped": skipped_count,
                "total": len(active_students)
            }

        except Exception as e:
            logger.error(f"Error generating monthly payments: {e}")
            return {"created": 0, "skipped": 0, "total": 0}

    @staticmethod
    def get_payment_statistics(
        db: Session,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> Dict:
        """
        Get payment statistics.

        Args:
            db: Database session
            month: Filter by month (optional)
            year: Filter by year (optional)

        Returns:
            Dict: Payment statistics
        """
        try:
            query = db.query(Payment)

            if month and year:
                query = query.filter(
                    and_(Payment.month == month, Payment.year == year)
                )

            total_payments = query.count()
            paid_payments = query.filter(Payment.status == "PAID").count()
            unpaid_payments = query.filter(Payment.status == "UNPAID").count()
            overdue_payments = query.filter(Payment.status == "OVERDUE").count()

            total_amount = db.query(db.func.sum(Payment.amount)).scalar() or 0
            paid_amount = db.query(db.func.sum(Payment.amount)).filter(Payment.status == "PAID").scalar() or 0

            return {
                "total_payments": total_payments,
                "paid_payments": paid_payments,
                "unpaid_payments": unpaid_payments,
                "overdue_payments": overdue_payments,
                "total_amount": float(total_amount),
                "paid_amount": float(paid_amount),
                "unpaid_amount": float(total_amount - paid_amount),
                "payment_rate": (paid_payments / total_payments * 100) if total_payments > 0 else 0
            }

        except Exception as e:
            logger.error(f"Error getting payment statistics: {e}")
            return {}

    @staticmethod
    def send_overdue_reminders(
        db: Session,
        days_overdue: int = 30
    ) -> Dict[str, int]:
        """
        Send payment reminders for overdue payments.

        Args:
            db: Database session
            days_overdue: Days past due date

        Returns:
            Dict[str, int]: Statistics about sent reminders
        """
        try:
            overdue_payments = PaymentService.get_overdue_payments(db, days_overdue)

            sent_count = 0
            failed_count = 0

            # Group by student to avoid duplicate notifications
            student_notifications = {}

            for payment in overdue_payments:
                if payment.student_id not in student_notifications:
                    student_notifications[payment.student_id] = payment

            for student_id, payment in student_notifications.items():
                if await NotificationService.send_payment_reminder(
                    db, student_id, payment.month, payment.year
                ):
                    sent_count += 1
                else:
                    failed_count += 1

            logger.info(f"Sent {sent_count} overdue payment reminders")

            return {
                "sent": sent_count,
                "failed": failed_count,
                "total_overdue": len(overdue_payments)
            }

        except Exception as e:
            logger.error(f"Error sending overdue reminders: {e}")
            return {"sent": 0, "failed": 0, "total_overdue": 0}

    @staticmethod
    def get_student_payment_history(
        db: Session,
        student_id: int,
        limit: int = 12
    ) -> List[Payment]:
        """
        Get payment history for a student.

        Args:
            db: Database session
            student_id: Student ID
            limit: Maximum number of records to return

        Returns:
            List[Payment]: Payment history
        """
        try:
            payments = db.query(Payment).filter(
                Payment.student_id == student_id
            ).order_by(
                Payment.year.desc(),
                Payment.month.desc()
            ).limit(limit).all()

            return payments

        except Exception as e:
            logger.error(f"Error getting payment history for student {student_id}: {e}")
            return []
