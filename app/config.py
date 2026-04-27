import json
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ShopBuilder API"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False

    platform_database_url: str
    tenant_database_urls: str = Field(
        description="JSON object mapping tenant database keys to DSNs",
        examples=['{"merchant_alpha":"postgresql+psycopg://postgres:postgres@postgres:5432/merchant_alpha"}'],
    )
    redis_url: str

    jwt_secret_key: str = Field(min_length=32)
    jwt_refresh_secret_key: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 7

    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://localhost:8000"])

    login_rate_limit_attempts: int = 5
    login_rate_limit_window_seconds: int = 60
    register_rate_limit_attempts: int = 5
    register_rate_limit_window_seconds: int = 60

    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30

    webhook_signing_secret: str = Field(min_length=32)
    theme_sandbox_mode: str = "strict"
    default_currency: str = "KZT"

    @field_validator("tenant_database_urls", mode="before")
    @classmethod
    def validate_tenant_database_urls(cls, value: str | dict[str, str]) -> str:
        if isinstance(value, dict):
            if len(value) < 2:
                raise ValueError("At least two tenant database URLs are required for ShopBuilder routing.")
            return json.dumps(value)

        parsed = json.loads(value)
        if not isinstance(parsed, dict) or len(parsed) < 2:
            raise ValueError("TENANT_DATABASE_URLS must be a JSON object with at least two entries.")
        return value

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            origins = value
        else:
            origins = [origin.strip() for origin in value.split(",") if origin.strip()]

        if not origins:
            raise ValueError("At least one CORS origin is required.")
        return origins

    @field_validator("jwt_algorithm")
    @classmethod
    def validate_algorithm(cls, value: str) -> str:
        allowed_algorithms = {"HS256"}
        if value not in allowed_algorithms:
            raise ValueError(f"JWT algorithm must be one of {sorted(allowed_algorithms)}.")
        return value

    @field_validator("app_env")
    @classmethod
    def validate_env(cls, value: str) -> str:
        allowed = {"development", "test", "production"}
        if value not in allowed:
            raise ValueError(f"APP_ENV must be one of {sorted(allowed)}.")
        return value

    @property
    def parsed_tenant_database_urls(self) -> dict[str, str]:
        return json.loads(self.tenant_database_urls)

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.is_production and "*" in settings.cors_origins:
        raise ValueError("Wildcard CORS origins are forbidden in production.")
    return settings


settings = get_settings()
