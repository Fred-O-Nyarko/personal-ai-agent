from typing import AsyncGenerator

from app.agents.base import BaseAgent
from app.agents.prebuilt.summarizer import SummarizerAgent
from app.llm.client import LLMClient
from app.tools.registry import ToolRegistry
from app.core.events import EventBus
from app.schemas.agent import RunRequest


class Orchestrator:
    """
    Routes incoming requests to the correct agent.
    Adding a new agent means adding one entry to _route() —
    nothing else changes.
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

    async def run(self, request: RunRequest) -> AsyncGenerator[str, None]:
        agent = self._route(request)
        async for chunk in agent.run(request):
            yield chunk

    def _route(self, request: RunRequest) -> BaseAgent:
        """
        Selects the appropriate agent based on the request.
        Currently routes everything to SummarizerAgent.
        Extend this as new agents are added.
        """
        return SummarizerAgent(
            llm_client=self._llm,
            tool_registry=self._registry,
            event_bus=self._bus,
        )