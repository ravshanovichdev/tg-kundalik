from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from data.config import botTOKEN
# from .middleware import SimpleMiddleware  # Временно отключено для aiogram 3.x


bot = Bot(token=botTOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())
# dp.middleware.setup(SimpleMiddleware())  # Временно отключено


