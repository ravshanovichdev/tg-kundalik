"""
Notification service for SamIT Global system.
Временная заглушка для локального тестирования Mini App.
"""
import logging
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for sending Telegram notifications.
    Временно отключено для локального тестирования.
    """

    @staticmethod
    async def send_message_to_user(
        db: Session,
        telegram_id: int,
        message: str
    ) -> bool:
        logger.info(f"Mock notification: {telegram_id} <- {message}")
        return True

    @staticmethod
    async def send_absence_notification(
        db: Session,
        student_id: int,
        absence_date: datetime,
        teacher_name: str = None
    ) -> bool:
        logger.info(f"Mock absence notification: student {student_id}, date {absence_date}")
        return True

    @staticmethod
    async def send_grade_notification(
        db: Session,
        grade_id: int
    ) -> bool:
        logger.info(f"Mock grade notification: grade {grade_id}")
        return True

    @staticmethod
    async def send_payment_reminder(
        db: Session,
        student_id: int
    ) -> bool:
        logger.info(f"Mock payment reminder: student {student_id}")
        return True

    @staticmethod
    async def send_bulk_notification(
        db: Session,
        user_ids: list,
        message: str
    ) -> bool:
        logger.info(f"Mock bulk notification: {len(user_ids)} users <- {message}")
        return True

    @staticmethod
    async def send_welcome_message(
        db: Session,
        telegram_id: int,
        full_name: str
    ) -> bool:
        logger.info(f"Mock welcome message: {telegram_id} ({full_name})")
        return True