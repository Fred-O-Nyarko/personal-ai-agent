from pydantic import BaseModel, HttpUrl
from fastapi import UploadFile


class RunRequest(BaseModel):
    url:       HttpUrl | None   = None
    file:      UploadFile | None = None
    thread_id: str | None       = None

    model_config = {"arbitrary_types_allowed": True}


class RunResponse(BaseModel):
    run_id:    str
    thread_id: str | None = None