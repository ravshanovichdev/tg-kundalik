"""
Telegram bot for SamIT Global notifications.
Bot is used ONLY for sending notifications to parents.
No interactive commands - all functionality is in the Mini App.
"""
import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data.config import botTOKEN

logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=botTOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Import handlers (will be used for notification sending)
# Note: Bot doesn't have interactive commands - only sends notifications
# All user interaction happens through the Telegram Mini App
