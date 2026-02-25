from typing import AsyncGenerator

from app.llm.base import LLMProvider


class LLMClient:
    """
    Provider-agnostic LLM client.
    Depends only on the LLMProvider interface — has zero knowledge
    of which concrete provider is active.
    Injected via the DI container.
    """

    def __init__(self, provider: LLMProvider) -> None:
        self._provider = provider

    async def complete(self, messages: list[dict]) -> str:
        return await self._provider.complete(messages)

    async def stream(self, messages: list[dict]) -> AsyncGenerator[str, None]:
        async for chunk in self._provider.stream(messages):
            yield chunk

    @property
    def model_name(self) -> str:
        return self._provider.get_model_name()

    def __repr__(self) -> str:
        return f"LLMClient(provider={self._provider!r})"