from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import StreamingResponse

from app.api.deps import get_agent_service
from app.schemas.agent import RunRequest
from app.services.agent_service import AgentService

router = APIRouter()

@router.post("/run")
async def run_agent(
    url: str | None = Form(None),
    file: UploadFile | None = File(None),
    thread_id: str | None = Form(None),
    service: AgentService = Depends(get_agent_service),
):
    """
    Start an agent run. Accepts either a URL or a PDF upload.
    Returns a Server-Sent Events stream.
    """

    request = RunRequest(url=url, file=file, thread_id=thread_id)

    return StreamingResponse(
        service.run(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control":     "no-cache",
            "X-Accel-Buffering": "no",       # disables Nginx buffering on Fly.io
        },
    )