# app/schemas/thread.py
from pydantic import BaseModel
from datetime import datetime


class ThreadCreate(BaseModel):
    title: str | None = None


class ThreadRead(BaseModel):
    id:         str
    title:      str | None
    created_at: datetime

    model_config = {"from_attributes": True}