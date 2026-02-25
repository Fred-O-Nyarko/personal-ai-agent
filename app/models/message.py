import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Text, ForeignKey
from app.models.thread import Base


class Message(Base):
    __tablename__ = "messages"

    id:         Mapped[str]      = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    thread_id:  Mapped[str]      = mapped_column(String, ForeignKey("threads.id", ondelete="CASCADE"))
    role:       Mapped[str]      = mapped_column(String)        # "user" | "assistant"
    content:    Mapped[str]      = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))