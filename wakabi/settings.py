from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    # PostgresDsn,
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    telegram_token: str = Field()

    # postgres_dsn: PostgresDsn = Field()

    pg_host: str = Field()

    pg_port: str = Field()

    pg_database: str = Field()

    pg_user: str = Field()

    pg_password: str = Field()

    training_answer_separator: str = "---"
