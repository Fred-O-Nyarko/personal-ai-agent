from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.thread import Thread
from app.models.message import Message
from app.schemas.thread import ThreadCreate
from app.core.exceptions import ThreadNotFoundError
from app.core.events import EventBus, ThreadCreatedEvent


class ThreadService:
    """Handles all thread and message CRUD operations."""

    def __init__(self, event_bus: EventBus) -> None:
        self._bus = event_bus

    async def create(self, db: AsyncSession, data: ThreadCreate) -> Thread:
        thread = Thread(title=data.title)
        db.add(thread)
        await db.commit()
        await db.refresh(thread)
        await self._bus.publish(ThreadCreatedEvent(thread_id=thread.id))
        return thread

    async def get(self, db: AsyncSession, thread_id: str) -> Thread:
        result = await db.execute(select(Thread).where(Thread.id == thread_id))
        thread = result.scalar_one_or_none()
        if not thread:
            raise ThreadNotFoundError(f"Thread '{thread_id}' not found.")
        return thread

    async def list_all(self, db: AsyncSession) -> list[Thread]:
        result = await db.execute(select(Thread).order_by(Thread.created_at.desc()))
        return list(result.scalars().all())

    async def delete(self, db: AsyncSession, thread_id: str) -> None:
        thread = await self.get(db, thread_id)
        await db.delete(thread)
        await db.commit()

    async def add_message(
        self,
        db:        AsyncSession,
        thread_id: str,
        role:      str,
        content:   str,
    ) -> Message:
        message = Message(thread_id=thread_id, role=role, content=content)
        db.add(message)
        await db.commit()
        await db.refresh(message)
        return message