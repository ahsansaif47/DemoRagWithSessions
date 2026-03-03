import os
from app.core.dependencies.config import AppConfig
from typing import List
from openai.types.chat import ChatCompletionUserMessageParam
from openai import AzureOpenAI

# TODO: Load this config where we want to initialize the client.
api_config = AppConfig().api_keys


class OpenAIClient:
    def __init__(self, model: str= "o4-mini"):
        self.openai_client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-12-01-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.model = model

    def generate_response(
            self,
            prompt: str,
    ):
        message:  List[ChatCompletionUserMessageParam] = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{prompt}"}
        ]
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,  # IMPORTANT: this is your DEPLOYMENT name, not model name
                messages=message,
            )

            return response.choices[0].message.content
        except Exception as e:
            raise e