import os
from pydantic import BaseModel, Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Annotated

print("DEBUG: Current environment variables:")
for key, value in os.environ.items():
    if 'BOT' in key or 'TOKEN' in key:
        print(f"DEBUG: {key} = {value}")

class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000



class DatabaseConfig(BaseModel):
    url: PostgresDsn = Field(  # Добавляем валидацию PostgreSQL DSN
        default="postgresql+asyncpg://user:password@pg:5432/learning_language",
        examples=["postgresql+asyncpg://user:password@host:port/dbname"]
    )
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 10
    max_overflow: int = 20


class BotConfig(BaseModel):
    token: str = Field(..., description="Telegram Bot Token")
    admin_ids: list[int] = Field(default_factory=list, description="Admin user IDs")

    @field_validator('token')
    @classmethod
    def validate_token(cls, v: str) -> str:
        if not v or len(v) < 10:
            raise ValueError("BOT_TOKEN must be valid")
        return v

class OpenAIConfig(BaseModel):
    api_key: str = Field(default="", description="OpenAI API Key")
    enabled: bool = Field(default=False, description="Enable OpenAI features")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore"
    )

    run: RunConfig = Field(default_factory=RunConfig)
    db: DatabaseConfig = Field(default_factory=DatabaseConfig)
    bot: Annotated[BotConfig, Field()]
    openai: OpenAIConfig = Field(default_factory=OpenAIConfig)


settings = Settings()
print(f"✓ Settings loaded: bot_token={settings.bot.token[:10]}...")
