"""
Notification service for SamIT Global system.
Handles Telegram notifications for parents about attendance, grades, and payments.
"""
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from bot.bot import bot
from models.user import User
from models.student import Student
from models.group import Group
from models.grade import Grade

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for sending Telegram notifications.
    Used by teachers and admins to notify parents.
    """

    @staticmethod
    async def send_message_to_user(
        db: Session,
        telegram_id: int,
        message: str
    ) -> bool:
        """
        Send message to a specific Telegram user.

        Args:
            db: Database session
            telegram_id: Telegram user ID
            message: Message text

        Returns:
            bool: Success status
        """
        try:
            await bot.send_message(
                chat_id=telegram_id,
                text=message,
                parse_mode='HTML'
            )
            logger.info(f"Notification sent to user {telegram_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send notification to user {telegram_id}: {e}")
            return False

    @staticmethod
    async def send_absence_notification(
        db: Session,
        student_id: int,
        absence_date: datetime
    ) -> bool:
        """
        Send notification to parent about student's absence.

        Args:
            db: Database session
            student_id: Student ID
            absence_date: Date of absence

        Returns:
            bool: Success status
        """
        try:
            # Get student and parent info
            student = db.query(Student).filter(Student.id == student_id).first()
            if not student:
                logger.error(f"Student {student_id} not found")
                return False

            parent = db.query(User).filter(User.id == student.parent_id).first()
            if not parent:
                logger.error(f"Parent for student {student_id} not found")
                return False

            # Get group info
            group = db.query(Group).filter(Group.id == student.group_id).first()

            # Format message
            date_str = absence_date.strftime("%d.%m.%Y")
            message = (
                f"🔔 <b>Уведомление о пропуске</b>\n\n"
                f"Ваш ребенок <b>{student.full_name}</b> "
                f"отсутствовал на занятии {date_str}.\n\n"
                f"📚 Группа: {group.name if group else 'Не указана'}\n"
                f"📅 Предмет: {group.subject if group else 'Не указан'}\n\n"
                f"Если это ошибка, пожалуйста, свяжитесь с преподавателем."
            )

            return await NotificationService.send_message_to_user(
                db, parent.telegram_id, message
            )

        except Exception as e:
            logger.error(f"Error sending absence notification for student {student_id}: {e}")
            return False

    @staticmethod
    async def send_grade_notification(
        db: Session,
        student_id: int,
        grade: Grade
    ) -> bool:
        """
        Send notification to parent about new grade.

        Args:
            db: Database session
            student_id: Student ID
            grade: Grade object

        Returns:
            bool: Success status
        """
        try:
            # Get student and parent info
            student = db.query(Student).filter(Student.id == student_id).first()
            if not student:
                logger.error(f"Student {student_id} not found")
                return False

            parent = db.query(User).filter(User.id == student.parent_id).first()
            if not parent:
                logger.error(f"Parent for student {student_id} not found")
                return False

            # Get group and teacher info
            group = db.query(Group).filter(Group.id == grade.group_id).first()
            teacher = db.query(User).filter(User.id == grade.given_by).first()

            # Format message
            date_str = grade.date_given.strftime("%d.%m.%Y")
            grade_display = f"{grade.value}"
            if grade.max_value != 5.0:
                grade_display += f"/{grade.max_value}"

            message = (
                f"📊 <b>Новая оценка</b>\n\n"
                f"Ваш ребенок <b>{student.full_name}</b> получил оценку:\n\n"
                f"🎯 <b>{grade_display}</b>\n"
                f"📝 Тип: {grade.type_display}\n"
                f"📚 Предмет: {group.subject if group else 'Не указан'}\n"
                f"👨‍🏫 Преподаватель: {teacher.full_name if teacher else 'Не указан'}\n"
                f"📅 Дата: {date_str}\n"
            )

            if grade.title:
                message += f"📋 Работа: {grade.title}\n"

            if grade.comment:
                message += f"\n💬 Комментарий: {grade.comment}\n"

            return await NotificationService.send_message_to_user(
                db, parent.telegram_id, message
            )

        except Exception as e:
            logger.error(f"Error sending grade notification for student {student_id}: {e}")
            return False

    @staticmethod
    async def send_payment_reminder(
        db: Session,
        student_id: int,
        month: int,
        year: int
    ) -> bool:
        """
        Send payment reminder to parent.

        Args:
            db: Database session
            student_id: Student ID
            month: Payment month
            year: Payment year

        Returns:
            bool: Success status
        """
        try:
            # Get student and parent info
            student = db.query(Student).filter(Student.id == student_id).first()
            if not student:
                logger.error(f"Student {student_id} not found")
                return False

            parent = db.query(User).filter(User.id == student.parent_id).first()
            if not parent:
                logger.error(f"Parent for student {student_id} not found")
                return False

            # Get group info for pricing
            group = db.query(Group).filter(Group.id == student.group_id).first()

            # Format month name
            months = [
                "января", "февраля", "марта", "апреля", "мая", "июня",
                "июля", "августа", "сентября", "октября", "ноября", "декабря"
            ]
            month_name = months[month - 1] if 1 <= month <= 12 else str(month)

            message = (
                f"💰 <b>Напоминание об оплате</b>\n\n"
                f"Уважаемый родитель!\n\n"
                f"Напоминаем об оплате обучения за {month_name} {year} г.\n\n"
                f"👨‍🎓 Ученик: <b>{student.full_name}</b>\n"
                f"📚 Группа: {group.name if group else 'Не указана'}\n"
                f"💵 Сумма: {group.monthly_price if group else 0} UZS\n\n"
                f"Просим произвести оплату в ближайшее время."
            )

            return await NotificationService.send_message_to_user(
                db, parent.telegram_id, message
            )

        except Exception as e:
            logger.error(f"Error sending payment reminder for student {student_id}: {e}")
            return False

    @staticmethod
    async def send_bulk_notification(
        db: Session,
        student_ids: list[int],
        message: str,
        subject: str = "Уведомление"
    ) -> dict:
        """
        Send bulk notification to multiple parents.

        Args:
            db: Database session
            student_ids: List of student IDs
            message: Message text
            subject: Message subject

        Returns:
            dict: Success statistics
        """
        success_count = 0
        fail_count = 0

        for student_id in student_ids:
            try:
                student = db.query(Student).filter(Student.id == student_id).first()
                if not student:
                    fail_count += 1
                    continue

                parent = db.query(User).filter(User.id == student.parent_id).first()
                if not parent:
                    fail_count += 1
                    continue

                # Format personalized message
                personalized_message = (
                    f"📢 <b>{subject}</b>\n\n"
                    f"Ученик: {student.full_name}\n\n"
                    f"{message}"
                )

                if await NotificationService.send_message_to_user(
                    db, parent.telegram_id, personalized_message
                ):
                    success_count += 1
                else:
                    fail_count += 1

            except Exception as e:
                logger.error(f"Error sending bulk notification to student {student_id}: {e}")
                fail_count += 1

        return {
            "total": len(student_ids),
            "success": success_count,
            "failed": fail_count
        }

    @staticmethod
    async def send_welcome_message(
        db: Session,
        telegram_id: int,
        user_name: str = None
    ) -> bool:
        """
        Send welcome message to new user.

        Args:
            db: Database session
            telegram_id: Telegram user ID
            user_name: User name for personalization

        Returns:
            bool: Success status
        """
        try:
            greeting = f", {user_name}" if user_name else ""

            message = (
                f"👋 <b>Добро пожаловать в SamIT Global{greeting}!</b>\n\n"
                f"🎓 Система управления учебным центром\n\n"
                f"Здесь вы можете:\n"
                f"• Следить за успеваемостью детей\n"
                f"• Просматривать посещаемость\n"
                f"• Получать уведомления об оценках\n"
                f"• Управлять платежами\n\n"
                f"Используйте Telegram Mini App для полного доступа к функциям."
            )

            return await NotificationService.send_message_to_user(
                db, telegram_id, message
            )

        except Exception as e:
            logger.error(f"Error sending welcome message to user {telegram_id}: {e}")
            return False
