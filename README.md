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
- PostgreSQL (рекомендуется версия 17.5 или выше)

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

   #### Выполните миграции, если они имеются.
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

5. **Разовая подготовка данных OSRM (роутинг по дорогам)**

   Делается один раз локально/на сервере, не на каждый рестарт.
   Тянуть `profiles/truck.lua` из основного репозитория OSRM бесполезно — такого файла там нет (404).
   Профиль `truck-soft` берём из официального репозитория
   [Project-OSRM/osrm-profiles-contrib (5/27/truck-soft)](https://github.com/Project-OSRM/osrm-profiles-contrib/tree/master/5/27/truck-soft);
   он подходит к образу `ghcr.io/project-osrm/osrm-backend:v5.27.1` (multi-arch: amd64/arm64).

   ```bash
   mkdir -p osrm/data osrm/profiles/lib
   curl -L -o osrm/data/region.osm.pbf https://download.geofabrik.de/europe/belarus-latest.osm.pbf
   curl -L -o osrm/profiles/truck.lua https://raw.githubusercontent.com/Project-OSRM/osrm-profiles-contrib/master/5/27/truck-soft/car.lua
   curl -L -o osrm/profiles/lib/way_handlers.lua https://raw.githubusercontent.com/Project-OSRM/osrm-profiles-contrib/master/5/27/truck-soft/lib/way_handlers.lua

   docker compose --profile tools run --rm osrm-prepare
   docker compose up -d osrm
   ```

   `osrm-extract` / `partition` / `customize` идут несколько минут (карта Беларуси ~350 МБ),
   результат складывается в `osrm/data/` (~2 ГБ, в git не попадает).
   Остальные модули профиля (`lib/set`, `lib/access`, ...) сервис `osrm-prepare` копирует из образа сам,
   поэтому кастомный `lib/way_handlers.lua` из `truck-soft` не перезаписывается.

   Проверка роутинга (Минск → Борисов):

   ```bash
   curl "http://localhost:5001/route/v1/driving/27.5615,53.9006;28.5,54.2279?overview=false"
   ```

   Бэкенд обращается к OSRM по `OSRM_URL` (в docker-сети `http://osrm:5000`, задаётся в `docker-compose.yml`).
   Чтобы обновить карту: удалить `osrm/data/region.osrm*`, скачать свежий `.osm.pbf` и повторить команды выше.

Теперь проект будет доступен по адресу `http://localhost:3000`.