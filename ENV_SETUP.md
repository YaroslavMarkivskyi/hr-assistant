# Налаштування змінних середовища

## Де зберігати змінні для Docker Compose?

Docker Compose автоматично читає файл `.env` з **кореня проекту** (там, де знаходиться `docker-compose.yml`).

## Швидкий старт

1. **Створіть файл `.env` в корені проекту:**

```bash
cd /home/yaroslav/work/teams-bot/hr-onboarding-assistant
touch .env
```

2. **Додайте свої змінні в `.env`:**

```bash
# Azure Bot Configuration
BOT_ID=73edfc17-255e-4d18-9aa0-5cd0284f9021
BOT_PASSWORD=your-secret-password
APP_TYPE=UserAssignedMsi
TEAMS_APP_TENANT_ID=688ec3e4-5d26-40e6-8b9a-2b609e8b360f

# OpenAI
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL_NAME=gpt-3.5-turbo

# Optional
TEST_USER_ID=dd69bb2d-2a60-4c15-a2ed-d30486cba374
DEFAULT_APPROVER=your-manager-id

# Environment Mode (for error handling)
# Set to "development" or "dev" or "local" for detailed error messages
# Leave empty or "production" for production (hides error details for security)
ENVIRONMENT=development
```

3. **Docker Compose автоматично підхопить змінні:**

```bash
docker-compose up -d
```

## Структура файлів

```
hr-onboarding-assistant/
├── .env                    # ← ТУТ зберігайте свої змінні (не комітьте в git!)
├── .env.example           # Приклад файлу
├── docker-compose.yml     # Читає .env автоматично
├── env/                   # Використовується для локальної розробки (не для Docker)
│   ├── .env
│   ├── .env.local
│   └── .env.local.user
└── ...
```

## Як це працює?

Docker Compose шукає `.env` файл в тому ж каталозі, де знаходиться `docker-compose.yml`, і автоматично підставляє значення змінних у форматі `${VARIABLE_NAME}`.

У `docker-compose.yml`:
```yaml
environment:
  - BOT_ID=${BOT_ID}  # ← Береться з .env файлу
```

## Перевірка змінних

```bash
# Перевірити, чи Docker Compose бачить змінні
docker-compose config

# Або запустити контейнер і перевірити всередині
docker-compose exec fastapi env | grep BOT_ID
```

## Безпека

- ✅ Файл `.env` вже додано в `.gitignore`
- ✅ Ніколи не комітьте `.env` в git
- ✅ Використовуйте `.env.example` як шаблон
- ✅ Для production використовуйте секрети Docker Swarm або Azure Key Vault

## Приклад .env файлу

Дивіться `.env.example` для повного списку доступних змінних.




