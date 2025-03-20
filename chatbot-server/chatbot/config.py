import os.path
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    openai_api_base: str = "https://api.openai.com/v1"
    chatbot_data_dir: str = "./data"
    chatbot_doc_store: str = os.path.join(chatbot_data_dir, "doc_store")
    chatbot_vector_store: str = os.path.join(chatbot_data_dir, "vector_store")
    chatbot_db_store: str = os.path.join(chatbot_data_dir, "db")

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
