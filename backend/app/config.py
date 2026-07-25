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

    analytics_events_file: Path = Path('storage/analytics/analytics_log.jsonl')
    analytics_photo_history_file: Path = Path('storage/analytics/photo_history.json')
    analytics_mismatch_file: Path = Path('storage/analytics/mismatch_log.json')
    analytics_news_cache_file: Path = Path('storage/analytics/news_cache.json')
    analytics_news_drafts_file: Path = Path('storage/analytics/news_drafts.json')
    analytics_ai_usage_file: Path = Path('storage/analytics/ai_usage_log.txt')
    analytics_runtime_metrics_file: Path | None = None

    # --- Честный знак / маркировка (модуль marking) ---
    # Окружение ГИС МТ: sandbox | production. По умолчанию sandbox.
    crpt_env: str = 'sandbox'
    # Базовые URL. Значения по умолчанию — песочница (см. docs/marking/crpt-api-mapping.md).
    crpt_true_api_base_url: str = 'https://markirovka.sandbox.crptech.ru/api/v3/true-api'
    crpt_true_api_v4_base_url: str = 'https://markirovka.sandbox.crptech.ru/api/v4/true-api'
    crpt_suz_base_url: str = 'https://markirovka.sandbox.crptech.ru'
    crpt_nk_base_url: str = 'https://апи.национальный-каталог.рф'
    # Явный предохранитель production. Без true продакшн-вызовы запрещены.
    crpt_allow_production: bool = False
    # Dry-run: юридически значимые операции не отправляются во внешние системы.
    crpt_dry_run: bool = True
    # Зашифрованное файловое хранилище КМ и чувствительных выгрузок.
    marking_storage_path: Path = Path('storage/marking')
    # Ключ шифрования (base64 urlsafe, 32 байта) для AES-GCM хранилища КМ и HMAC km_hash.
    marking_encryption_key: str = ''
    # Sign Agent (подпись через выносной агент CryptoPro).
    sign_job_ttl_seconds: int = 900
    sign_agent_poll_seconds: int = 5
    # Таймаут HTTP-клиентов ГИС МТ, секунды.
    crpt_http_timeout: float = 30.0


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
