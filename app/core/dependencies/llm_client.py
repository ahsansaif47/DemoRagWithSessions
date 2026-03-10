from app.integrations.llm.local_openai import OpenAIClient
from functools import lru_cache
from fastapi import Request


# TODO: Change this to an initializer and a getter function


def init_openai_client():
    return OpenAIClient()

@lru_cache
def get_openai_client(request: Request) -> OpenAIClient:
    return request.app.state.openai_client