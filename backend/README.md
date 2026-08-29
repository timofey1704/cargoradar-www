# Backend для CargoRadar - архитектура приложения FastAPI + SQLAlchemy 2.0 + Alembic + Pydantic

## Структура проекта:

app/
├── main.py                  # сборка app, CORS, include_router
├── core/
│   ├── config.py            # Settings из .env через pydantic-settings
│   ├── database.py          # async engine + AsyncSessionLocal + Base
│   ├── security.py          # bcrypt + JWT encode/decode
│   └── dependencies.py      # get_db, get_current_user → DbSession, CurrentUser
├── models/                  # SQLAlchemy 2.0 (Mapped[], mapped_column)
├── schemas/                 # Pydantic — валидация входа и форма ответа
├── repositories/            # только SQL-запросы, никакой логики
├── services/                # вся бизнес-логика, HTTPException живут здесь
└── routers/                 # тонкие, только HTTP: принял → вызвал сервис → вернул

## Базовые команды:

1. **Запустить виртуальное окружение:**
   ```sh
   source .venv/bin/activate
   ```

2. **Обновить все зависимости до последней версии:**
   ```sh
   uv sync --upgrade
   ```

3. **Запустить локальный сервер:**
   ```sh
   uv run uvicorn main:app --reload
   ```

## Через Docker:
1. **Запустить проект:**
   ```sh
   docker compose up
   ```

2. **Установить пакеты:**
   ```sh
   docker compose exec backend uv add <package>
   ```
   Если dev-зависимость, то:
   ```sh
   docker compose exec backend uv add --dev pytest
   ```

3. **Удалить пакеты:**
   ```sh
   docker compose exec backend uv remove <package>
   ```
   
4. **Обновить все зависимости до последней версии:**
   ```sh
   docker compose exec backend uv sync --upgrade
   ```

## Миграции:

### Рабочий цикл миграции

1. **Поменял модель, например добавил поле username в User**
2. **Генерируешь миграцию**

```sh
   docker compose exec backend uv run alembic revision --autogenerate -m "description"
   ```

3. **Смотришь что сгенерировалось (важно!) в migrations/versions/**
Alembic иногда ошибается, особенно с индексами и constraints

4. **Применяешь**
docker compose exec backend uv run alembic upgrade head

### Nice to know:
1. **Какая миграция сейчас в БД:**
 ```sh
   docker compose exec backend uv run alembic current
   ```

2. **История всех миграций:**
 ```sh
   docker compose exec backend uv run alembic history
   ```

3. **Откатить последнюю миграцию:**
 ```sh
   docker compose exec backend uv run alembic downgrade -1
   ```
