from sqlalchemy.ext.asyncio import AsyncSession
from app.models.run import Run
from app.core.exceptions import RunNotFoundError
from sqlalchemy import select


class RunService:
    """Tracks the lifecycle of each agent run."""

    async def create(
        self,
        db:        AsyncSession,
        tool_used: str,
        thread_id: str | None = None,
    ) -> Run:
        run = Run(tool_used=tool_used, thread_id=thread_id, status="running")
        db.add(run)
        await db.commit()
        await db.refresh(run)
        return run

    async def complete(self, db: AsyncSession, run_id: str, token_usage: int) -> Run:
        run = await self._get(db, run_id)
        run.status      = "done"
        run.token_usage = token_usage
        await db.commit()
        return run

    async def fail(self, db: AsyncSession, run_id: str) -> Run:
        run = await self._get(db, run_id)
        run.status = "failed"
        await db.commit()
        return run

    async def _get(self, db: AsyncSession, run_id: str) -> Run:
        result = await db.execute(select(Run).where(Run.id == run_id))
        run    = result.scalar_one_or_none()
        if not run:
            raise RunNotFoundError(f"Run '{run_id}' not found.")
        return run