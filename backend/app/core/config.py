from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str
    # This fallback keeps local development startup working; deployments must override it.
    jwt_secret: str = "development-only-insecure-placeholder"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    dev_user_id: str | None = None
    market_price_cache_seconds: int = 300

    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        extra = "ignore"
    )

settings = Settings()