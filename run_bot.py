#!/usr/bin/env python3
"""
SamIT Global Bot Launcher
Запуск Telegram бота для уведомлений
"""
import sys
import os

# Добавляем корневую папку в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Запуск бота"""
    try:
        print("🚀 Запуск SamIT Global Bot...")

        # Импортируем и запускаем бота
        from main import executor, dp

        print("✅ Бот успешно инициализирован")
        print("📱 Нажмите Ctrl+C для остановки")

        # Запускаем polling
        executor.start_polling(dp, skip_updates=True)

    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
