import os
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DB_URL: str
    TEST_DB_URL: str
    ACCESS_TOKEN_EXPIRY: int
    REFRESH_TOKEN_EXPIRY: int
    SECRET_KEY: str

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        if os.getenv("RUN_ENV") == "test":
            return self.TEST_DB_URL
        return self.DB_URL


@lru_cache
def get_settings():
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]

settings = get_settings()
