from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    openai_api_base: str = "https://api.openai.com/v1"

    class Config:
        env_file = ".env"
        env_prefix = "OPENAI_"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
