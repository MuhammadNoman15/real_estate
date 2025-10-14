from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # Tell pydantic to load .env and ignore extra env vars
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")

    postgres_user: str = Field(default="realestate", alias="POSTGRES_USER")
    postgres_password: str = Field(default="realestate_password", alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="realestate", alias="POSTGRES_DB")
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")

    google_maps_api_key: str | None = Field(default=None, alias="GOOGLE_MAPS_API_KEY")
    translink_api_key: str | None = Field(default=None, alias="TRANSLINK_API_KEY")

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    llm_provider: str | None = Field(default=None, alias="LLM_PROVIDER")


settings = Settings()  # type: ignore


def get_database_url() -> str:
    return (
        f"postgresql+psycopg2://{settings.postgres_user}:{settings.postgres_password}"
        f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
    )
