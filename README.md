# SamIT Global - Telegram Mini App

Educational center management system built as a Telegram Mini App with FastAPI backend and React frontend.

## 🚀 Features

- **Telegram Mini App**: Web application that runs inside Telegram
- **Role-based access**: Admin, Teacher, and Parent dashboards
- **Student management**: Add, edit, and manage student information
- **Attendance tracking**: Mark and view student attendance
- **Grade management**: Assign and track student grades
- **Payment tracking**: Monitor student payments
- **Notifications**: Automated notifications to parents via Telegram bot
- **Responsive design**: Works on all devices through Telegram

## 🛠️ Tech Stack

- **Backend**: FastAPI, SQLAlchemy, MySQL
- **Frontend**: React, Telegram Web App API
- **Bot**: aiogram (Python Telegram Bot API)
- **Database**: MySQL
- **Deployment**: Docker-ready

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- MySQL database
- Telegram Bot Token (from @BotFather)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd tg-kundalik
```

### 2. Environment Configuration

```bash
# Copy environment template
cp env-example.txt .env

# Edit .env file with your settings
nano .env
```

Required environment variables:
- `TELEGRAM_BOT_TOKEN`: Your bot token from @BotFather
- `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`: Database settings
- `WEBAPP_URL`: Your Mini App domain (e.g., https://your-app.com)
- `SECRET_KEY`: Random secret key for JWT

### 3. Telegram Bot Setup

1. **Create bot with @BotFather**:
   ```
   /newbot
   Bot name: SamIT Global
   Username: your_bot_username
   ```

2. **Enable Mini App**:
   ```
   /setmenubutton
   Bot username: @your_bot_username
   Menu button URL: https://your-domain.com
   Menu button text: Открыть приложение
   ```

### 4. Install Dependencies

```bash
# Python dependencies
pip install -r requirements.txt

# Frontend dependencies
cd frontend && npm install && cd ..
```

### 5. Database Setup

```bash
# Create MySQL database
mysql -u root -p
CREATE DATABASE samit_global;
exit

# Run database migrations (if any)
python -c "from app.database import init_database; init_database()"
```

### 6. Build and Run

```bash
# Make startup script executable
chmod +x start_all.sh

# Run the complete system
./start_all.sh
```

The system will start on:
- **Mini App**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🔧 Manual Setup

### Backend Only

```bash
cd app
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Bot Only

```bash
python run_bot.py
```

### Frontend Development

```bash
cd frontend
npm start
```

## 📱 Telegram Mini App Configuration

### BotFather Commands

After creating your bot, configure the Mini App menu button:

```
/setmenubutton
Bot: @your_bot_username
Button URL: https://your-domain.com
Button text: 🚀 Открыть приложение
```

### Web App URL

Update the `WEBAPP_URL` in your `.env` file to match your production domain.

### Testing Locally

For local testing, you can use ngrok or similar to expose your localhost:

```bash
# Install ngrok
npm install -g ngrok

# Expose port 8000
ngrok http 8000

# Use the ngrok URL in BotFather and .env
```

## 🏗️ Project Structure

```
tg-kundalik/
├── app/                    # FastAPI backend
│   ├── main.py            # Main FastAPI app
│   ├── config.py          # Configuration
│   ├── database.py        # Database setup
│   └── static/            # Built frontend files
├── bot/                   # Telegram bot
│   ├── bot.py            # Bot configuration
│   └── handlers/         # Bot command handlers
├── frontend/             # React frontend
│   ├── src/
│   ├── build/           # Built files
│   └── package.json
├── models/               # SQLAlchemy models
├── routers/              # API endpoints
├── schemas/              # Pydantic schemas
└── requirements.txt      # Python dependencies
```

## 🔒 Security

- Telegram WebApp data validation
- JWT token authentication
- Role-based access control
- Input validation and sanitization

## 📊 API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support, contact the development team or create an issue in the repository. - Educational Center Management System

Полнофункциональное MVP Telegram Mini App для управления учебным центром (аналог kundalik.com).

## 🚀 Возможности

### 👥 Роли пользователей

**Администратор:**
- ✅ CRUD пользователей (преподаватели, родители, ученики)
- ✅ Управление группами и ценами
- ✅ Управление платежами
- ✅ Отправка уведомлений

**Преподаватель:**
- ✅ Отметка посещаемости (Присутствовал/Отсутствовал/Опоздал)
- ✅ Выставление оценок с комментариями
- ✅ Автоматические уведомления родителям

**Родитель:**
- ✅ Просмотр данных только своих детей
- ✅ Посещаемость и оценки
- ✅ Средний балл и статус платежей

## 🏗 Архитектура

```
📁 app/                     # FastAPI backend
├── main.py                # Точка входа приложения
├── config.py              # Конфигурация
├── database.py            # Подключение к БД
├── routers/               # API endpoints
│   ├── auth.py           # Аутентификация
│   ├── admin.py          # Админ функции
│   ├── teacher.py        # Функции преподавателя
│   └── parent.py         # Функции родителя
├── schemas/              # Pydantic модели
├── services/             # Бизнес логика
└── models/               # SQLAlchemy модели

📁 bot/                    # Telegram бот (уведомления)
├── bot.py                # Основной бот
├── handlers/             # Обработчики команд
└── keyboards.py          # Клавиатуры

📁 frontend/              # React Mini App
├── src/
│   ├── pages/           # Страницы дашбордов
│   ├── components/      # Переиспользуемые компоненты
│   └── services/        # API клиент
└── package.json

📁 data/                  # Конфигурация и утилиты
└── config.py            # Переменные окружения
```

## 🛠 Технологии

### Backend
- **FastAPI** - Асинхронный веб-фреймворк
- **SQLAlchemy** - ORM для работы с БД
- **Pydantic** - Валидация данных
- **MySQL** - База данных

### Frontend
- **React** - UI фреймворк
- **Telegram WebApp API** - Интеграция с Telegram

### Bot
- **aiogram** - Telegram Bot API
- Только для уведомлений

## 🚀 Быстрый запуск

### 1. Клонирование и установка зависимостей

```bash
# Backend зависимости
pip install -r requirements.txt

# Frontend зависимости
cd frontend
npm install
cd ..
```

### 2. Настройка переменных окружения

Создайте файл `.env`:

```env
# Database
MYSQL_HOST=localhost
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=samit_global

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token

# Application
SECRET_KEY=your-secret-key
WEBAPP_URL=https://your-domain.com
```

### 3. Запуск

```bash
# Backend (FastAPI)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (React) - в другом терминале
cd frontend
npm start

# Bot (уведомления) - в третьем терминале
python main.py
```

### 4. Доступ

- **API Documentation**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **Bot**: Через Telegram

## 🔐 Аутентификация

Приложение использует Telegram WebApp аутентификацию:
- Пользователь идентифицируется по `telegram_id`
- Ролевая модель доступа (admin/teacher/parent)
- JWT токены для API запросов

## 📊 База данных

### Основные таблицы
- `users` - Пользователи системы
- `students` - Ученики
- `teachers` - Преподаватели
- `groups` - Учебные группы
- `attendance` - Посещаемость
- `grades` - Оценки
- `payments` - Платежи

### Автоматические действия
- **Отсутствие**: Автоматическое уведомление родителя
- **Оценки**: Уведомление родителя о новой оценке
- **Платежи**: Напоминания о просрочке

## 🎯 MVP Функционал

### ✅ Реализовано
- Полная аутентификация через Telegram
- Ролевая система доступа
- CRUD операции для всех ролей
- Telegram уведомления
- Responsive React интерфейс
- REST API с документацией

### 🎨 UI/UX
- Адаптивный дизайн для мобильных
- Telegram Mini App интеграция
- Интуитивный интерфейс для каждой роли

## 📝 API Endpoints

### Аутентификация
- `GET /api/auth/me` - Текущий пользователь
- `POST /api/auth/verify` - Проверка токена

### Администратор
- `GET /api/admin/users` - Список пользователей
- `POST /api/admin/groups` - Создать группу
- `POST /api/admin/payments` - Создать платеж

### Преподаватель
- `GET /api/teacher/groups` - Группы преподавателя
- `POST /api/teacher/attendance` - Отметить посещаемость
- `POST /api/teacher/grades` - Выставить оценку

### Родитель
- `GET /api/parent/children` - Дети родителя
- `GET /api/parent/children/{id}/grades` - Оценки ребенка
- `GET /api/parent/dashboard` - Дашборд

## 🤝 Contributing

1. Fork проект
2. Создайте feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit изменения (`git commit -m 'Add some AmazingFeature'`)
4. Push в branch (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. Подробности в файле `LICENSE`.

## 👥 Команда

- **Senior Full-Stack Developer** - Архитектура и разработка
- **UI/UX Designer** - Дизайн интерфейсов
- **QA Engineer** - Тестирование

## 📞 Контакты

- **Email**: info@samit-global.uz
- **Telegram**: @samit_global_bot
- **Website**: https://samit-global.uz

---

⭐ Если проект оказался полезным, поставьте звезду на GitHub!
