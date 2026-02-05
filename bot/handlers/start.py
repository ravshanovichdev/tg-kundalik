"""
Start handler for SamIT Global Telegram bot.
Handles /start command and welcomes users to the Mini App.
"""
import logging
from aiogram import types
from sqlalchemy.orm import Session

from bot.bot import dp
from bot.keyboards import get_welcome_keyboard
from data.db import Users
from services.notification_service import NotificationService
from app.database import SessionLocal

logger = logging.getLogger(__name__)


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    """
    Handle /start command.
    Registers user and shows welcome message with Mini App link.
    """
    try:
        telegram_id = message.from_user.id
        username = message.from_user.username
        full_name = message.from_user.full_name

        # Register user in database
        db: Session = SessionLocal()
        try:
            # Use existing database functions
            Users.ensure_user(telegram_id, username or str(telegram_id))

            # Send welcome message via notification service
            await NotificationService.send_welcome_message(
                db, telegram_id, full_name
            )

        finally:
            db.close()

        # Send welcome message with keyboard
        welcome_text = (
            f"👋 <b>Добро пожаловать в SamIT Global!</b>\n\n"
            f"🎓 Система управления учебным центром\n\n"
            f"Для доступа ко всем функциям используйте наше приложение:"
        )

        await message.reply(
            welcome_text,
            reply_markup=get_welcome_keyboard()
        )

        logger.info(f"User {telegram_id} started bot")

    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        await message.reply(
            "❌ Произошла ошибка. Попробуйте позже.",
            reply_markup=get_welcome_keyboard()
        )


@dp.message_handler(commands=['help'])
async def cmd_help(message: types.Message):
    """
    Handle /help command.
    Shows help information.
    """
    try:
        help_text = (
            f"🆘 <b>Помощь</b>\n\n"
            f"🎓 <b>SamIT Global</b> - система управления учебным центром\n\n"
            f"📱 <b>Основные функции:</b>\n"
            f"• Управление учениками и группами\n"
            f"• Отметка посещаемости\n"
            f"• Выставление оценок\n"
            f"• Уведомления родителям\n"
            f"• Управление платежами\n\n"
            f"🚀 Все функции доступны в приложении!"
        )

        from bot.keyboards import get_help_keyboard
        await message.reply(
            help_text,
            reply_markup=get_help_keyboard()
        )

    except Exception as e:
        logger.error(f"Error in help handler: {e}")
        await message.reply("❌ Произошла ошибка при получении справки.")


@dp.message_handler(commands=['app'])
async def cmd_app(message: types.Message):
    """
    Handle /app command.
    Direct link to Mini App.
    """
    try:
        app_text = (
            f"🚀 <b>Открыть приложение SamIT Global</b>\n\n"
            f"Нажмите кнопку ниже для перехода в приложение:"
        )

        await message.reply(
            app_text,
            reply_markup=get_welcome_keyboard()
        )

    except Exception as e:
        logger.error(f"Error in app handler: {e}")
        await message.reply("❌ Произошла ошибка.")


# Handle unknown commands
@dp.message_handler()
async def handle_unknown(message: types.Message):
    """
    Handle unknown messages and commands.
    Bot is notification-only, so redirect to Mini App.
    """
    try:
        # Don't respond to unknown messages to avoid spam
        # But log them for debugging
        logger.info(f"Unknown message from user {message.from_user.id}: {message.text}")

        # Optionally send a brief hint (uncomment if needed)
        # hint_text = "🤖 Для доступа к функциям используйте приложение!"
        # await message.reply(hint_text, reply_markup=get_welcome_keyboard())

    except Exception as e:
        logger.error(f"Error handling unknown message: {e}")