import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Integer, ForeignKey
from app.models.thread import Base


class Run(Base):
    __tablename__ = "runs"

    id:          Mapped[str]      = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    thread_id:   Mapped[str|None] = mapped_column(String, ForeignKey("threads.id", ondelete="CASCADE"), nullable=True)
    tool_used:   Mapped[str]      = mapped_column(String)
    status:      Mapped[str]      = mapped_column(String, default="pending")   # pending | running | done | failed
    token_usage: Mapped[int]      = mapped_column(Integer, default=0)
    created_at:  Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))