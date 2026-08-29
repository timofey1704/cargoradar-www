# Cargoradar

Добро пожаловать в репозиторий сайта Cargo Radar. Этот проект включает в себя фронтенд на Next.js и бэкенд на FastAPI с базой данных PostgreSQL.

## Описание

Проект предоставляет возможность перевозчикам и отправителям искать друг друга.

## Технологии

### Фронтенд

- **Next.js** - библиотека для создания пользовательских интерфейсов.

### Бэкенд

- **FastAPI** - веб-фреймворк для Python.
- **PostgreSQL** - реляционная база данных для хранения данных.

## Установка

### Предварительные требования

Для запуска проекта вам потребуются:

- Node.js (рекомендуется версия 24.x или выше)
- Python (рекомендуется версия 3.14 или выше)
- PostgreSQL (рекомендуется версия 17.x или выше)

### Шаги для установки

1. **Клонирование репозитория:**

   ```sh
   git clone https://github.com/timofey1704/cargoradar-www.git
   cd cargoradar-www
   ```

2. **Установка Docker:**

   ```sh
   https://docs.docker.com/desktop/setup/install/mac-install/
   ```

3. **Запуск проекта:**

   В корневой директории проекта выполните команду:

   ```sh
   docker compose up
   ```
   
   # Выполните миграции, если они имеются.
   ```sh
   cd backend
   docker compose exec backend uv run alembic upgrade head
   ```

4. **Настройка переменных окружения:**

   Создайте файл `.env` в директории `backend` и добавьте необходимые переменные окружения:

   ```env
   POSTGRES_PASSWORD=
   DATABASE_URL=postgresql+asyncpg://{login}:{password}@postgres:5432/{database_name}
   SECRET_KEY=
   REFRESH_SECRET_KEY=
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=30
   ```

Теперь проект будет доступен по адресу `http://localhost:3000`.