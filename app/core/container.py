from functools import lru_cache

from app.config import get_settings, Settings
from app.core.events import (
    EventBus,
    RunStartedEvent,
    RunCompletedEvent,
    RunFailedEvent,
    ToolCalledEvent,
    ThreadCreatedEvent
)
from app.core.logger import StructuredLogger

class Container:
    """
    Single source of truth for all wired dependencies.
    Built once at app startup via the lifespan in main.py.
    All FastAPI routes receive dependencies from here via Depends().
    """

    def __init__(self, settings: Settings)-> None:
        self.settings = settings
        self._event_bus: EventBus = EventBus()
        self._logger: StructuredLogger = StructuredLogger()
        self._wire_observers()


    # ── Observers ─────────────────────────────────────────────────────────────

    def _wire_observers(self) -> None:
        """Subscribe all logger handlers to the event bus."""
        bus = self._event_bus
        bus.subscribe(RunStartedEvent, self._logger.on_run_started)
        bus.subscribe(RunCompletedEvent, self._logger.on_run_completed)
        bus.subscribe(RunFailedEvent, self._logger.on_run_failed)
        bus.subscribe(ToolCalledEvent, self._logger.on_tool_called)
        bus.subscribe(ThreadCreatedEvent, self._logger.on_thread_created)


    # ── Properties ─────────────────────────────────────────────────────────────

    @property
    def event_bus(self) -> EventBus:
        return self._event_bus


    # ── LLM (built lazily — provider not needed until first request) ──────────

    @property
    def llm_client(self):
        if not hasattr(self, '_llm_client'):
            from app.llm.factory import LLMProviderFactory
            from app.llm.client import LLMClient
            provider = LLMProviderFactory.create(self.settings.llm_provider)
            self._llm_client = LLMClient(provider=provider)
        return self._llm_client


    # ── Tools ─────────────────────────────────────────────────────────────────

    @property
    def tool_registry(self):
        if not hasattr(self, "_tool_registry"):
            from app.tools.registry import ToolRegistry
            from app.tools.url_scraper import URLScraperTool
            from app.tools.pdf_reader import PDFReaderTool
            registry = ToolRegistry(event_bus=self._event_bus)
            registry.register(URLScraperTool())
            registry.register(PDFReaderTool())
            self._tool_registry = registry
        return self._tool_registry


    # ── Services ──────────────────────────────────────────────────────────────

    @property
    def agent_service(self):
        if not hasattr(self, "_agent_service"):
            from app.services.agent_service import AgentService
            self._agent_service = AgentService(
                llm_client=self.llm_client,
                tool_registry=self.tool_registry,
                event_bus=self._event_bus,
            )
        return self._agent_service

    @property
    def thread_service(self):
        if not hasattr(self, "_thread_service"):
            from app.services.thread_service import ThreadService
            self._thread_service = ThreadService()
        return self._thread_service


@lru_cache
def get_container() -> Container:
    return Container(settings=get_settings())