from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: SecretStr = SecretStr("postgresql+psycopg://postgres:postgres@localhost:5432/postgres")
    jwt_secret: SecretStr = Field(min_length=32)
    token_minutes: int = Field(default=30, ge=1, le=1440)
    cors_origins: list[str] = Field(default_factory=list)


settings = Settings()
