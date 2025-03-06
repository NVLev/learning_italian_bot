from pydantic import BaseModel, Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


# = Field(..., description="Database URL")


class DatabaseConfig(BaseModel):
    url: PostgresDsn = Field(  # Добавляем валидацию PostgreSQL DSN
        default="postgresql+asyncpg://user:password@pg:5432/learning_language",
        examples=["postgresql+asyncpg://user:password@host:port/dbname"]
    )
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 10
    max_overflow: int = 20


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore"
    )

    run: RunConfig = RunConfig()
    db: DatabaseConfig = DatabaseConfig()


settings = Settings()
