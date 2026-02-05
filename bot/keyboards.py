"""
Telegram bot keyboards for SamIT Global.
Since bot is used ONLY for notifications, keyboards are minimal.
All main functionality is in the Telegram Mini App.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_welcome_keyboard() -> InlineKeyboardMarkup:
    """
    Welcome keyboard with link to Mini App.
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(
            text="🚀 Открыть приложение",
            web_app={"url": "https://your-mini-app-domain.com"}  # Replace with your actual domain
        )
    )
    return keyboard


def get_notification_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard for notification messages.
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(
            text="📱 Открыть приложение",
            web_app={"url": "https://your-mini-app-domain.com"}  # Replace with your actual domain
        )
    )
    return keyboard


def get_help_keyboard() -> InlineKeyboardMarkup:
    """
    Help keyboard with useful links.
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(
            text="🚀 Приложение",
            web_app={"url": "https://your-mini-app-domain.com"}  # Replace with your actual domain
        ),
        InlineKeyboardButton(
            text="📞 Поддержка",
            url="https://t.me/YOUR_SUPPORT_USERNAME"
        )
    )
    return keyboard
