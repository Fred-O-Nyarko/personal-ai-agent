from abc import ABC, abstractmethod
from openai.types.chat import ChatCompletionMessageParam


class BaseMemory(ABC):
    """
    Swappable memory interface.
    Currently implemented as short-term in-context memory.
    TODO: Extend for long-term vector DB memory later.
    """

    @abstractmethod
    def add(self, role: str, content: str) -> None:
        """Add a message to memory."""
        ...

    @abstractmethod
    def get(self) -> list[ChatCompletionMessageParam]:
        """Return all messages in memory."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Wipe memory — called at end of session or thread."""
        ...

    @abstractmethod
    def __len__(self) -> int:
        """Return number of messages currently in memory."""
        ...