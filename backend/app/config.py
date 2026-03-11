from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'ProstoMark API'
    app_env: str = 'development'
    debug: bool = False
    api_v1_prefix: str = '/api/v1'

    database_url: str = Field(default='postgresql+psycopg2://postgres:postgres@postgres:5432/prostomark')
    redis_url: str = Field(default='redis://redis:6379/0')

    jwt_secret: str = Field(default='change_me')
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30

    cors_origins: str = 'http://localhost:5173,http://localhost'

    storage_path: Path = Path('storage')

    stripe_secret_key: str = ''
    stripe_webhook_secret: str = ''
    stripe_success_url: str = 'http://localhost/billing/success'
    stripe_cancel_url: str = 'http://localhost/billing/cancel'

    openai_api_key: str = ''
    openai_model: str = 'gpt-4o-mini'

    smtp_host: str = ''
    smtp_port: int = 587
    smtp_user: str = ''
    smtp_pass: str = ''
    smtp_from: str = 'noreply@prostomark.local'


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
