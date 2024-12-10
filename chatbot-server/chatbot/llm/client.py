from functools import lru_cache
from openai import AsyncOpenAI

from chatbot.config import get_settings

@lru_cache()
def get_client() -> AsyncOpenAI:
    settings = get_settings()
    return AsyncOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_api_base
    )

