from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LIBRARY_", extra="ignore")

    api_key: str


@lru_cache
def get_settings() -> Settings:
    # pydantic-settings populates api_key from LIBRARY_API_KEY at runtime;
    # mypy does not model that source, so it reports api_key as a missing argument.
    return Settings()  # type: ignore[call-arg]


def __getattr__(name: str) -> Settings:
    if name == "settings":
        return get_settings()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
