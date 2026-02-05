#!/bin/bash

# SamIT Global - Запуск всех компонентов системы
echo "🚀 Запуск SamIT Global системы..."

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден!"
    echo "📝 Скопируйте env-example.txt в .env и заполните настройки"
    exit 1
fi

# Проверка Python зависимостей
echo "📦 Проверка Python зависимостей..."
if ! python -c "import fastapi, sqlalchemy, aiogram" 2>/dev/null; then
    echo "❌ Python зависимости не установлены!"
    echo "📝 Запустите: pip install -r requirements.txt"
    exit 1
fi

echo "✅ Python зависимости установлены"

# Сборка frontend если нужно
if [ ! -d "app/static" ] || [ ! -f "app/static/index.html" ]; then
    echo "📦 Сборка frontend для Mini App..."
    cd frontend
    if command -v npm &> /dev/null; then
        npm install
        npm run build
        cd ..
        mkdir -p app/static
        cp -r frontend/build/* app/static/
        echo "✅ Frontend собран успешно"
    else
        echo "⚠️ npm не найден, frontend не собран"
    fi
fi

# Запуск Backend (FastAPI)
echo "🔧 Запуск Backend API..."
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "✅ Backend запущен (PID: $BACKEND_PID)"

# Ожидание запуска backend
sleep 3

# Запуск бота в фоне
echo "🤖 Запуск Telegram Bot..."
python run_bot.py &
BOT_PID=$!
echo "✅ Bot запущен (PID: $BOT_PID)"

# Информация о запуске
echo ""
echo "🎉 Система SamIT Global запущена!"
echo ""
echo "📊 Доступ:"
echo "   • API: http://localhost:8000"
echo "   • Docs: http://localhost:8000/docs"
echo "   • Bot: работает в Telegram"
echo ""
echo "🛑 Для остановки нажмите Ctrl+C"

# Функция очистки при выходе
cleanup() {
    echo ""
    echo "🛑 Остановка системы..."
    kill $BACKEND_PID 2>/dev/null
    kill $BOT_PID 2>/dev/null
    echo "✅ Система остановлена"
    exit 0
}

# Обработка сигналов
trap cleanup SIGINT SIGTERM

# Ожидание
wait
