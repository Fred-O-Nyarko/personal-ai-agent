from abc import ABC, abstractmethod
from typing import AsyncGenerator

from app.llm.client import LLMClient
from app.tools.registry import ToolRegistry
from app.core.events import EventBus


class BaseAgent(ABC):
    """
    All agents extend this class.
    Receives its dependencies via DI — never constructs them directly.
    """

    def __init__(
        self,
        llm_client:    LLMClient,
        tool_registry: ToolRegistry,
        event_bus:     EventBus,
    ) -> None:
        self._llm      = llm_client
        self._registry = tool_registry
        self._bus      = event_bus

    @abstractmethod
    async def run(self, request) -> AsyncGenerator[str, None]:
        """
        Execute the agent and yield SSE-formatted chunks.
        Implemented by each concrete agent.
        """
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self._llm.model_name!r})"