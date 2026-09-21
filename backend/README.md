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

## Кеширование GET-ответов (Redis)

Данные, которые редко меняются (FAQ главной, каталог тарифов), кешируются в Redis,
чтобы не ходить в БД на каждый запрос. Всё лежит в `core/`:

- `core/redis/cache.py` — декоратор `@cached(ttl, key)` и хелпер `cache_key("main:faq")`
- `core/redis/get_cached_json.py`, `set_cached_json.py` — чтение/запись JSON в кеш
- `core/redis/delete_cached_keys.py`, `delete_cached_by_prefix.py` — инвалидация
- методы-обёртки в `RedisClient`: `get_cached_json`, `set_cached_json`,
  `delete_cached_keys`, `delete_cached_by_prefix`

### Как закешировать метод сервиса

```python
from core.config import settings
from core.redis.cache import cached


class MainPageService:
    @cached(ttl=settings.cache_ttl_faq, key="main:faq")
    async def get_faqs(self) -> list[FAQRead]:
        faqs = await self.repository.get_faqs()
        return [FAQRead.model_validate(faq) for faq in faqs]
```

- декоратор работает только с `async`-функциями и берёт тип из аннотации возврата,
  поэтому из кеша приходят те же модели Pydantic (`list[FAQRead]`), что и без кеша;
- ключ — строка или билдер: `@cached(ttl=60, key=lambda user_id: f"user:{user_id}")`;
- ключ автоматически префиксуется `CACHE_PREFIX` (по умолчанию `cache:`).

### Инвалидация

```python
from core.redis.cache import cache_key
from core.redis.redis_client import redis_client

await redis_client.delete_cached_keys(cache_key("main:faq"))       # точечно
await redis_client.delete_cached_by_prefix(settings.cache_prefix)  # всё сразу
```

### Настройки (.env)

| Переменная | По умолчанию | Что делает |
|---|---|---|
| `CACHE_ENABLED` | `true` | выключает кеш целиком (удобно при отладке) |
| `CACHE_PREFIX` | `cache:` | общий префикс ключей кеша |
| `CACHE_TTL_FAQ` | `300` | TTL для FAQ главной |
| `CACHE_TTL_MEMBERSHIP_PLANS` | `300` | TTL для каталога тарифов |

Redis — ускоритель, а не источник правды: ошибки Redis и битый/устаревший кеш
игнорируются, метод просто выполняется как обычно (тесты `core/tests/test_cache_decorator.py`).

### Тесты

```sh
docker compose exec backend uv run pytest core/tests -q            # всё, включая integration
docker compose exec backend uv run pytest -m "not integration" -q  # без живого Redis
```
