# Docker Setup Guide

Цей гайд допоможе вам запустити HR Bot через Docker з PostgreSQL та підключити його до Microsoft Teams через ngrok.

## Передумови

- Docker та Docker Compose встановлені
- ngrok встановлений та налаштований
- Azure Bot зареєстрований в Azure Portal
- Змінні середовища налаштовані в `env/.env`

## Крок 1: Налаштування змінних середовища

**Docker Compose автоматично читає `.env` файл з кореня проекту.**

Створіть файл `.env` в корені проекту (поруч з `docker-compose.yml`):

```bash
# Скопіюйте приклад
cp .env.example .env

# Або створіть вручну
touch .env
```

Додайте свої змінні в `.env` файл:

```bash
# Azure Bot Configuration
BOT_ID=your-bot-id-here
BOT_PASSWORD=your-bot-password-here
APP_TYPE=UserAssignedMsi
TEAMS_APP_TENANT_ID=your-tenant-id

# OpenAI
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL_NAME=gpt-3.5-turbo

# Optional: Email Service
COMMUNICATION_CONNECTION_STRING=your-connection-string
MAIL_FROM_ADDRESS=noreply@example.com

# Optional: Development
TEST_USER_ID=your-test-user-id
DEFAULT_APPROVER=your-manager-id

# Environment Mode (for error handling)
# Set to "development", "dev", or "local" for detailed error messages in API responses
# Leave empty or "production" for production (hides error details for security)
ENVIRONMENT=development
```

**Важливо:**
- Файл `.env` знаходиться в **корені проекту** (поруч з `docker-compose.yml`)
- Docker Compose автоматично читає цей файл
- Файл `.env` вже додано в `.gitignore` - не комітьте його в git!
- Для прикладу використовуйте `.env.example`

## Крок 2: Запуск Docker Compose

```bash
# Запустити всі сервіси (FastAPI + PostgreSQL)
docker-compose up -d

# Переглянути логи
docker-compose logs -f fastapi

# Зупинити сервіси
docker-compose down

# Зупинити та видалити volumes (очистити БД)
docker-compose down -v
```

## Крок 3: Налаштування ngrok

ngrok потрібен для того, щоб Microsoft Teams міг підключитися до вашого локального FastAPI сервера.

### Встановлення ngrok

```bash
# macOS
brew install ngrok

# Linux
# Завантажте з https://ngrok.com/download
# або через snap
snap install ngrok

# Windows
# Завантажте з https://ngrok.com/download
```

### Запуск ngrok

```bash
# Запустити ngrok tunnel на порт 8000
ngrok http 8000

# Або з доменом (якщо у вас є платний план)
ngrok http 8000 --domain=your-domain.ngrok.io
```

Після запуску ngrok покаже URL типу:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8000
```

### Налаштування Azure Bot

1. Відкрийте [Azure Portal](https://portal.azure.com)
2. Перейдіть до вашого Bot Service
3. В розділі **Configuration** знайдіть **Messaging endpoint**
4. Встановіть URL: `https://your-ngrok-url.ngrok.io/api/messages`
5. Збережіть зміни

## Крок 4: Перевірка підключення

### Перевірка FastAPI

```bash
# Health check
curl http://localhost:8000/health

# Root endpoint
curl http://localhost:8000/
```

### Перевірка PostgreSQL

```bash
# Підключитися до PostgreSQL
docker-compose exec postgres psql -U hr_bot_user -d hr_bot

# Перевірити таблиці
\dt
```

### Перевірка Teams Bot

1. Відкрийте Microsoft Teams
2. Знайдіть ваш бот
3. Надішліть повідомлення: "Привіт"
4. Перевірте логи: `docker-compose logs -f fastapi`

## Структура Docker

```
hr-onboarding-assistant/
├── Dockerfile              # FastAPI контейнер
├── docker-compose.yml      # Оркестрація сервісів
├── .dockerignore          # Файли для ігнорування
└── src/
    └── main.py            # FastAPI додаток
```

## Troubleshooting

### Проблема: Бот не відповідає в Teams

1. Перевірте, чи працює ngrok:
   ```bash
   curl https://your-ngrok-url.ngrok.io/health
   ```

2. Перевірте логи FastAPI:
   ```bash
   docker-compose logs fastapi
   ```

3. Перевірте, чи правильно налаштований Messaging endpoint в Azure Portal

### Проблема: Помилка підключення до PostgreSQL

1. Перевірте, чи запущений контейнер:
   ```bash
   docker-compose ps
   ```

2. Перевірте логи PostgreSQL:
   ```bash
   docker-compose logs postgres
   ```

3. Перевірте змінні середовища в `docker-compose.yml`

### Проблема: Помилки при збірці Docker

1. Очистіть кеш Docker:
   ```bash
   docker system prune -a
   ```

2. Перебудуйте образи:
   ```bash
   docker-compose build --no-cache
   ```

## Production Deployment

Для production deployment:

1. Використовуйте реальний домен замість ngrok
2. Налаштуйте HTTPS сертифікат
3. Використовуйте Azure Database for PostgreSQL замість локального контейнера
4. Налаштуйте Azure Container Instances або Azure App Service
5. Додайте моніторинг та логування

## Додаткові команди

```bash
# Перебудувати образи
docker-compose build

# Перезапустити сервіси
docker-compose restart

# Видалити всі контейнери та volumes
docker-compose down -v

# Виконати команду в контейнері
docker-compose exec fastapi python -c "from config import Config; print(Config().APP_ID)"

# Переглянути використання ресурсів
docker stats
```

