from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.container import get_container
from app.db.session import build_engine, build_session_factory


def get_event_bus():
    return get_container().event_bus

def get_llm_client():
    return get_container().llm_client

def get_tool_registry():
    return get_container().tool_registry


def get_agent_service():
    return get_container().agent_service


def get_thread_service():
    return get_container().thread_service


# ── Database session per request ──────────────────────────────────────────────
_engine  = build_engine()
_factory = build_session_factory(_engine)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with _factory() as session:
        yield session