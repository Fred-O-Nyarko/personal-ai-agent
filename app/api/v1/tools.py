from fastapi import APIRouter, Depends

from app.api.deps import get_tool_registry
from app.tools.registry import ToolRegistry

router = APIRouter()


@router.get("")
async def list_tools(registry: ToolRegistry = Depends(get_tool_registry)):
    """Return all registered tools and their schemas."""
    return {"tools": registry.list_all()}