from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = ""
    secret_key: SecretStr = SecretStr("")
    refresh_secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30
    
    # redis — смс-коды верификации и другие временные данные
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    # короткие таймауты: если Redis лежит, смс-флоу не должен ждать
    redis_connect_timeout: float = 1.0
    redis_command_timeout: float = 2.0
    # сколько раз повторить команду при обрыве соединения (повторы без пауз)
    redis_retry_count: int = 3

    # OSRM — расчёт маршрутов/километража по дорогам (в docker-сети задаётся в compose)
    osrm_url: str = "http://localhost:5000"

    # кеш ответов GET-роутов — для данных, которые редко меняются
    cache_enabled: bool = True
    cache_prefix: str = "cache:"
    cache_ttl_faq: int = 86400  # секунд
    cache_ttl_membership_plans: int = 86400  # секунд
    cache_ttl_search: int = 300  # секунд
    
    # админские токены — свои TTL (панелью пользуются реже, но сессию держать удобнее)
    admin_access_token_expire_minutes: int = 60
    admin_refresh_token_expire_days: int = 30
    
    # токены исполнителей 
    admin_access_token_expire_minutes: int = 30
    admin_refresh_token_expire_days: int = 30

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if len(self.secret_key.get_secret_value()) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")


settings = Settings()