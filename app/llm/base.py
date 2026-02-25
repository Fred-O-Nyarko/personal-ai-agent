from abc import ABC, abstractmethod
from typing import AsyncGenerator

class LLMProvider(ABC):
    """
    Strategy interface — every LLM provider must implement this contract.
    Agents and services depend only on this abstraction, never on a
    concrete provider class.
    """

    @abstractmethod
    async def complete(self, messages: list[dict])-> str:
        """Single-shot completion. Returns the full response as a string."""
        ...

    @abstractmethod
    async def stream(self, messages: list[dict])-> AsyncGenerator[str, None]:
        """
        Streaming completion.
        Yields SSE-formatted strings ready to send to the client.
        """
        ...

    @abstractmethod
    def get_model_name(self) -> str:
        """Return the active model identifier string."""
        ...

    def __repr__(self)->str:
        return f"{self.__class__.__name__}(model={self.get_model_name()!r})"