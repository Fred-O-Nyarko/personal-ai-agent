from pydantic import BaseModel
from datetime import datetime


class MessageRead(BaseModel):
    id:         str
    thread_id:  str
    role:       str
    content:    str
    created_at: datetime

    model_config = {"from_attributes": True}