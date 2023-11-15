from pydantic import Field, PostgresDsn
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="local.env", env_file_encoding="utf-8", extra='ignore')

    telegram_token: str = Field()
    pg_dsn: PostgresDsn = Field()

    training_answer_separator: str = "---"
