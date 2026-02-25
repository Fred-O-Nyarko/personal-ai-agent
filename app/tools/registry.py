from app.tools.base import BaseTool, ToolInput, ToolOutput
from app.core.events import EventBus, ToolCalledEvent
from app.core.exceptions import ToolNotFoundError


class ToolRegistry:
    """
    Factory + Registry.
    Decouples agents from concrete tool classes entirely.
    Agents call registry.execute('tool_name', input) —
    they never import or instantiate tools directly.
    """

    def __init__(self, event_bus: EventBus) -> None:
        self._tools:    dict[str, BaseTool] = {}
        self._event_bus = event_bus

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        tool = self._tools.get(name)
        if not tool:
            raise ToolNotFoundError(
                f"Tool '{name}' not found. Registered: {self.list_names()}"
            )
        return tool

    def list_names(self) -> list[str]:
        return list(self._tools.keys())

    def list_all(self) -> list[dict]:
        return [t.schema() for t in self._tools.values()]

    async def execute(self, name: str, input: ToolInput) -> ToolOutput:
        tool = self.get(name)
        await self._event_bus.publish(ToolCalledEvent(
            tool=name,
            input=str(input),
        ))
        return await tool.execute(input)
