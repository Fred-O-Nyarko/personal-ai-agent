from dataclasses import dataclass, field
from typing import Callable, Awaitable, Any
import uuid

def _new_id() -> str:
    return str(uuid.uuid4())

# ── Base ──────────────────────────────────────────────────────────────────────

@dataclass
class BaseEvent:
    correlation_id: str = field(default_factory=_new_id)


# ── Run Events ────────────────────────────────────────────────────────────────

@dataclass
class RunStartedEvent(BaseEvent):
    run_id: str = ""
    tool: str = ""
    input: str = ""

@dataclass
class RunCompletedEvent(BaseEvent):
    run_id: str = ""
    tokens_used: str = ""

@dataclass
class RunFailedEvent(BaseEvent):
    run_id: str = ""
    error: str = ""
    code: str = ""


# ── Tool Events ───────────────────────────────────────────────────────────────

@dataclass
class ToolCalledEvent(BaseEvent):
    tool: str = ""
    input: str = ""

@dataclass
class TokenEvent(BaseEvent):
    tool: str = ""


# ── Thread Events ─────────────────────────────────────────────────────────────

@dataclass
class ThreadCanceledEvent(BaseEvent):
    thread_id: str = ""

@dataclass
class ThreadCreatedEvent(BaseEvent):
    thread_id: str = ""


# ── Bus ───────────────────────────────────────────────────────────────────────

class EventBus:
    """
    Observer pattern implementation.
    Publishers and subscribers are fully decoupled -
    neither knows the other exists.
    """

    def __init__(self) -> None:
        self._handlers = dict[type, list[Callable[..., Awaitable[None]]]]()

    def subscribe(self, event_type: type[BaseEvent], handler: Callable[..., Awaitable[None]]) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    async def publish(self, event: BaseEvent) -> None:
        for handler in self._handlers.get(type(event), []):
            await handler(event)