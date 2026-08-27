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

## Миграции:

### Рабочий цикл миграции

1. **Поменял модель, например добавил поле username в User**
2. **Генерируешь миграцию**

```sh
   uv run alembic revision --autogenerate -m "add username to user"
   ```

3. **Смотришь что сгенерировалось (важно!) в migrations/versions/**
Alembic иногда ошибается, особенно с индексами и constraints

4. **Применяешь**
uv run alembic upgrade head

### Nice to know:
1. **Какая миграция сейчас в БД:**
 ```sh
   uv run alembic current 
   ```

2. **История всех миграций:**
 ```sh
   uv run alembic history 
   ```

3. **Откатить последнюю миграцию:**
 ```sh
   uv run alembic downgrade -1
   ```
