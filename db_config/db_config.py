from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


# = Field(..., description="Database URL")


class DatabaseConfig(BaseModel):
    url: str
    echo: bool = True
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10
    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class Settings(BaseSettings):
    # model_config = SettingsConfigDict(
    #     env_file=(".env.template", ".env"),
    #     case_sensitive=False,
    #     env_nested_delimiter="__",
    #     env_prefix="CONFIG__",
    # )
    run: RunConfig = RunConfig()
    db: DatabaseConfig = DatabaseConfig(
        url="postgresql+asyncpg://user:password@localhost:5432/recipes"
    )


settings = Settings()