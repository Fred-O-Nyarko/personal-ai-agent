import json
from typing import AsyncGenerator

from openai import AsyncOpenAI, APIError, APIConnectionError, RateLimitError
from openai.types.chat import ChatCompletionMessageParam

from app.llm.base import LLMProvider
from app.core.exceptions import LLMError, LLMStreamError
from app.config import get_settings


class OpenAIProvider(LLMProvider):
    """Concrete Strategy — wraps the OpenAI async client."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model  = settings.openai_model

    async def complete(self, messages: list[ChatCompletionMessageParam]) -> str:
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
            )
            return response.choices[0].message.content or ""
        except RateLimitError as e:
            raise LLMError(f"OpenAI rate limit reached: {e}") from e
        except APIConnectionError as e:
            raise LLMError(f"Could not connect to OpenAI: {e}") from e
        except APIError as e:
            raise LLMError(f"OpenAI API error: {e}") from e

    async def stream(self, messages: list[ChatCompletionMessageParam]) -> AsyncGenerator[str, None]:
        try:
            async with self._client.chat.completions.stream(
                model=self._model,
                messages=messages,
            ) as s:
                async for chunk in s:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        yield f"data: {json.dumps({'type': 'token', 'content': delta})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except RateLimitError as e:
            yield f"data: {json.dumps({'type': 'error', 'code': 'RATE_LIMIT', 'message': str(e)})}\n\n"
            raise LLMStreamError(f"OpenAI rate limit during stream: {e}") from e
        except APIError as e:
            yield f"data: {json.dumps({'type': 'error', 'code': 'LLM_ERROR', 'message': str(e)})}\n\n"
            raise LLMStreamError(f"OpenAI stream error: {e}") from e

    def get_model_name(self) -> str:
        return self._model