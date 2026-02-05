import logging
import logging.config
import os
from aiogram import executor
from data.logs import LOGGING_CONFIG
from bot import dp
from bot import handlers  # noqa: F401  # регистрируем обработчики

if not os.path.exists("logs"):
    os.makedirs("logs")

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)