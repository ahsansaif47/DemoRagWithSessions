from app.integrations.llm.local_openai import OpenAIClient
from functools import lru_cache

@lru_cache
def get_openai_client() -> OpenAIClient:
    return OpenAIClient()