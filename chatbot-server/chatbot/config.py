import os.path
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    openai_api_base: str = "https://api.openai.com/v1"
    chatbot_data_dir: str = "./data"
    chatbot_docs_dir: str = os.path.join(chatbot_data_dir, "docs")

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
