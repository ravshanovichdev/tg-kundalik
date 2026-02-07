# Docker Setup для SamIT Global

## 🐳 Быстрый старт

### 1. Подготовка

```bash
# Скопируйте пример файла окружения
cp .env.example .env

# Отредактируйте .env файл с вашими настройками
nano .env
```

### 2. Запуск

```bash
# Собрать и запустить все сервисы
docker-compose up -d

# Или с пересборкой
docker-compose up -d --build
```

### 3. Проверка

- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Database: localhost:3306

## 📋 Команды

### Основные команды

```bash
# Запустить все сервисы
make up
# или
docker-compose up -d

# Остановить все сервисы
make down
# или
docker-compose down

# Просмотр логов
make logs
# или
docker-compose logs -f

# Перезапустить сервисы
make restart
# или
docker-compose restart
```

### Работа с базой данных

```bash
# Инициализировать базу данных (создать таблицы)
make db-init

# Сбросить базу данных (УДАЛИТ ВСЕ ДАННЫЕ!)
make db-reset
```

### Разработка

```bash
# Запустить в режиме разработки (с hot-reload)
make dev
# или
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## 🗄️ База данных

### Подключение к MySQL

```bash
# Через docker-compose
docker-compose exec db mysql -u samit_user -p samit_global

# Или напрямую
mysql -h localhost -P 3306 -u samit_user -p samit_global
```

### Пароли по умолчанию

- Root password: `rootpassword` (из .env)
- User: `samit_user`
- Password: `samit_password`
- Database: `samit_global`

**⚠️ ВАЖНО: Измените пароли в production!**

## 🔧 Структура сервисов

### Backend (FastAPI)
- Порт: 8000
- Health check: http://localhost:8000/health
- API Docs: http://localhost:8000/docs

### Frontend (React + Nginx)
- Порт: 3000
- Статические файлы обслуживаются через Nginx

### Database (MySQL 8.0)
- Порт: 3306
- Данные сохраняются в volume `mysql_data`

### Bot (Telegram Bot)
- Запускается только с профилем `bot`
- Команда: `docker-compose --profile bot up bot`

## 🔐 Переменные окружения

Основные переменные в `.env`:

```env
# Database
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_USER=samit_user
MYSQL_PASSWORD=samit_password
MYSQL_DATABASE=samit_global

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token

# Application
SECRET_KEY=your-secret-key
WEBAPP_URL=http://localhost:3000
```

## 🧹 Очистка

```bash
# Удалить все контейнеры и volumes
make clean

# Удалить только volumes
docker-compose down -v
```

## 📝 Troubleshooting

### Проблема: База данных не подключается

```bash
# Проверить статус базы данных
docker-compose ps db

# Проверить логи
docker-compose logs db

# Перезапустить базу данных
docker-compose restart db
```

### Проблема: Backend не может подключиться к БД

Убедитесь, что:
1. База данных запущена: `docker-compose ps db`
2. Переменные окружения правильные в `.env`
3. Backend ждет готовности БД (healthcheck)

### Проблема: Frontend не видит Backend

1. Проверьте `REACT_APP_API_URL` в docker-compose.yml
2. Убедитесь, что backend доступен на порту 8000
3. Проверьте CORS настройки в backend

## 🚀 Production Deployment

Для production:

1. Измените все пароли в `.env`
2. Установите `DEBUG=false`
3. Используйте HTTPS для `WEBAPP_URL`
4. Настройте правильные CORS origins
5. Используйте secrets для чувствительных данных

```bash
# Production build
docker-compose -f docker-compose.yml build --no-cache

# Production run
docker-compose -f docker-compose.yml up -d
```

