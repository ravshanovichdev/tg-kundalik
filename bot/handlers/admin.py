"""
Admin handlers for SamIT Global Telegram bot.
Provides admin commands for bot management and notifications.
"""
import logging
from aiogram import types
from sqlalchemy.orm import Session

from bot.bot import dp
from data.db import Users
from app.database import SessionLocal
from services.notification_service import NotificationService
from services.payment_service import PaymentService

logger = logging.getLogger(__name__)


def is_admin(telegram_id: int, db: Session) -> bool:
    """
    Check if user is admin.
    """
    user = Users.getUserById(telegram_id)
    return user and user.get('role') == 'admin'


@dp.message_handler(commands=['admin'])
async def cmd_admin(message: types.Message):
    """
    Admin panel access.
    """
    try:
        db: Session = SessionLocal()
        try:
            if not is_admin(message.from_user.id, db):
                await message.reply("❌ У вас нет доступа к админ-панели.")
                return

            admin_text = (
                f"🔧 <b>Админ-панель SamIT Global</b>\n\n"
                f"📊 <b>Доступные команды:</b>\n"
                f"/stats - Статистика системы\n"
                f"/notify_all - Отправить уведомление всем\n"
                f"/generate_payments - Сгенерировать платежи за месяц\n"
                f"/overdue_reminders - Отправить напоминания о просрочке\n\n"
                f"🚀 Все функции доступны в приложении!"
            )

            await message.reply(admin_text)

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in admin command: {e}")
        await message.reply("❌ Произошла ошибка.")


@dp.message_handler(commands=['stats'])
async def cmd_stats(message: types.Message):
    """
    Show system statistics.
    """
    try:
        db: Session = SessionLocal()
        try:
            if not is_admin(message.from_user.id, db):
                await message.reply("❌ Доступ запрещен.")
                return

            # Get user stats
            user_stats = Users.getStats()

            # Get payment stats for current month
            from datetime import datetime
            current_month = datetime.now().month
            current_year = datetime.now().year

            payment_stats = PaymentService.get_payment_statistics(db, current_month, current_year)

            stats_text = (
                f"📊 <b>Статистика системы</b>\n\n"
                f"👥 <b>Пользователи:</b>\n"
                f"• Всего: {user_stats.get('total_users', 0)}\n"
                f"• Активных: {user_stats.get('total_users', 0) - user_stats.get('blocked_users', 0)}\n"
                f"• Заблокированных: {user_stats.get('blocked_users', 0)}\n"
                f"• Новых за неделю: {user_stats.get('new_users_week', 0)}\n\n"
                f"💰 <b>Платежи ({current_month}.{current_year}):</b>\n"
                f"• Всего платежей: {payment_stats.get('total_payments', 0)}\n"
                f"• Оплачено: {payment_stats.get('paid_payments', 0)}\n"
                f"• Не оплачено: {payment_stats.get('unpaid_payments', 0)}\n"
                f"• Процент оплаты: {payment_stats.get('payment_rate', 0):.1f}%\n"
            )

            await message.reply(stats_text)

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in stats command: {e}")
        await message.reply("❌ Ошибка получения статистики.")


@dp.message_handler(commands=['notify_all'])
async def cmd_notify_all(message: types.Message):
    """
    Send notification to all users.
    Usage: /notify_all <message>
    """
    try:
        db: Session = SessionLocal()
        try:
            if not is_admin(message.from_user.id, db):
                await message.reply("❌ Доступ запрещен.")
                return

            # Parse message
            command_parts = message.text.split(' ', 2)
            if len(command_parts) < 3:
                await message.reply("❌ Использование: /notify_all <сообщение>")
                return

            notification_message = command_parts[2]

            # Get all active users
            all_users = Users.getAllUsers()
            active_users = [u for u in all_users if u.get('isBlocked') == 0]

            # Send notifications
            sent_count = 0
            for user in active_users:
                telegram_id = user.get('userId')
                if await NotificationService.send_message_to_user(
                    db, telegram_id, f"📢 <b>Уведомление от администрации</b>\n\n{notification_message}"
                ):
                    sent_count += 1

            await message.reply(
                f"✅ Уведомление отправлено {sent_count} из {len(active_users)} пользователей."
            )

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in notify_all command: {e}")
        await message.reply("❌ Ошибка отправки уведомлений.")


@dp.message_handler(commands=['generate_payments'])
async def cmd_generate_payments(message: types.Message):
    """
    Generate payment records for current month.
    Usage: /generate_payments [month] [year]
    """
    try:
        db: Session = SessionLocal()
        try:
            if not is_admin(message.from_user.id, db):
                await message.reply("❌ Доступ запрещен.")
                return

            # Parse parameters
            command_parts = message.text.split()
            current_date = datetime.now()

            if len(command_parts) >= 3:
                try:
                    month = int(command_parts[1])
                    year = int(command_parts[2])
                except ValueError:
                    await message.reply("❌ Неверный формат месяца/года. Используйте числа.")
                    return
            else:
                month = current_date.month
                year = current_date.year

            # Generate payments
            result = PaymentService.generate_monthly_payments(db, month, year)

            await message.reply(
                f"✅ Сгенерированы платежи за {month}.{year}\n"
                f"• Создано: {result['created']}\n"
                f"• Пропущено: {result['skipped']}\n"
                f"• Всего учеников: {result['total']}"
            )

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in generate_payments command: {e}")
        await message.reply("❌ Ошибка генерации платежей.")


@dp.message_handler(commands=['overdue_reminders'])
async def cmd_overdue_reminders(message: types.Message):
    """
    Send overdue payment reminders.
    Usage: /overdue_reminders [days_overdue]
    """
    try:
        db: Session = SessionLocal()
        try:
            if not is_admin(message.from_user.id, db):
                await message.reply("❌ Доступ запрещен.")
                return

            # Parse parameters
            command_parts = message.text.split()
            days_overdue = 30  # Default

            if len(command_parts) >= 2:
                try:
                    days_overdue = int(command_parts[1])
                except ValueError:
                    await message.reply("❌ Неверный формат дней. Используйте число.")
                    return

            # Send reminders
            result = await PaymentService.send_overdue_reminders(db, days_overdue)

            await message.reply(
                f"✅ Отправлены напоминания о просрочке\n"
                f"• Отправлено: {result['sent']}\n"
                f"• Ошибок: {result['failed']}\n"
                f"• Просроченных платежей: {result['total_overdue']}\n"
                f"• Дни просрочки: {days_overdue}"
            )

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in overdue_reminders command: {e}")
        await message.reply("❌ Ошибка отправки напоминаний.")
