from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LIBRARY_", extra="ignore")

    api_key: str = "dev-key"


settings = Settings()
