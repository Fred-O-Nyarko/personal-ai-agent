import logging
import sys
from pythonjsonlogger.json import JsonFormatter

from app.core.events import (
    RunStartedEvent,
    RunCompletedEvent,
    RunFailedEvent,
    ToolCalledEvent,
    ThreadCreatedEvent,
)

def setup_logging(log_level: str = "INFO") -> None:
    """Call once at app startup in main.py lifespan."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s"
    ))
    root = logging.getLogger()
    root.setLevel(log_level.upper())
    root.handlers = [handler]

def get_logger(name: str) -> logging.Logger:
    """Get a named logger. Use the module name: get_logger(__name__"""
    return logging.getLogger(name)

class StructuredLogger:
    """
    Observer subscriber — wired to EventBus in container.py.
    Reacts to system events and writes structured JSON logs.
    Never imported by agents or tools directly.
    """

    def __init__(self) -> None:
        self._log = get_logger(__name__)

    async def on_run_started(self, event: RunStartedEvent) -> None:
        self._log.info("run_started", extra={
            "correlation_id": event.correlation_id,
            "run_id": event.run_id,
            "tool": event.tool,
        })

    async def on_run_completed(self, event: RunCompletedEvent) -> None:
        self._log.info("run_completed", extra={
            "correlation_id": event.correlation_id,
            "run_id": event.run_id,
            "tokens_used": event.tokens_used,
        })

    async def on_run_failed(self, event: RunFailedEvent) -> None:
        self._log.error("run_failed", extra={
            "correlation_id": event.correlation_id,
            "run_id": event.run_id,
            "error": event.error,
            "code": event.code,
        })

    async def on_tool_called(self, event: ToolCalledEvent) -> None:
        self._log.info("tool_called", extra={
            "correlation_id": event.correlation_id,
            "thread_id": event.tool
        })

    async def on_thread_created(self, event: ThreadCreatedEvent) -> None:
        self._log.info("thread_created", extra={
            "correlation_id": event.correlation_id,
            "thread_id": event.thread_id,
        })