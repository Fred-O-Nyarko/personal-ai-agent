import json
from typing import AsyncGenerator

from app.agents.orchestrator import Orchestrator
from app.llm.client import LLMClient
from app.tools.registry import ToolRegistry
from app.core.events import EventBus
from app.schemas.agent import RunRequest
from build.lib.app.core.exceptions import BaseAppError


class AgentService:
    """
    Business logic layer between the API and the agent orchestrator.
    Owns the run lifecycle — validation, orchestration, persistence hooks.
    """

    def __init__(
        self,
        llm_client:    LLMClient,
        tool_registry: ToolRegistry,
        event_bus:     EventBus,
    ) -> None:
        self._orchestrator = Orchestrator(
            llm_client=llm_client,
            tool_registry=tool_registry,
            event_bus=event_bus,
        )

    async def run(self, request: RunRequest) -> AsyncGenerator[str, None]:
        if not request.url and not request.file:
            raise ValueError("Request must include either a url or a file.")

        try:
            async for chunk in self._orchestrator.run(request):
                yield chunk
        except BaseAppError as e:
            # yield a clean SSE error event instead of crashing the stream
            yield f"data: {json.dumps({'type': 'error', 'code': e.code, 'message': e.message})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'code': 'INTERNAL_ERROR', 'message': str(e)})}\n\n"
