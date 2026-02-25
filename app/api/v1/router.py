from fastapi import APIRouter

from app.api.v1 import agents, threads, tools

router = APIRouter()

router.include_router(agents.router, prefix="/agents", tags=["Agents"])
router.include_router(threads.router, prefix="/threads", tags=["Threads"])
router.include_router(tools.router, prefix="/tools", tags=["Tools"])