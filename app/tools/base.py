from abc import ABC, abstractmethod
from pydantic import BaseModel

class ToolInput(BaseModel):
    """Base input - all tool inputs extend this."""
    pass

class ToolOutput(BaseModel):
    """Base output - all tool outputs extend this."""
    content: str
    metadata: dict = {}

class BaseTool(ABC):
    """
    Strategy interface — every tool must implement execute().
    Agents never import concrete tool classes directly.
    They call the registry by name.
    """

    name:        str
    description: str

    @abstractmethod
    async def execute(self, input: ToolInput) -> ToolOutput:
        ...

    def schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"