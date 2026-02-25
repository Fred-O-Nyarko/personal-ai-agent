from openai.types.chat import ChatCompletionMessageParam
from app.memory.base import BaseMemory


class InContextMemory(BaseMemory):
    """
    Stores conversation history as a plain list in memory.
    Lives for the duration of a single request/session.
    Pass an instance per thread to maintain separate histories.
    """

    def __init__(self, max_messages: int = 20) -> None:
        self._messages:     list[ChatCompletionMessageParam] = []
        self._max_messages: int = max_messages

    def add(self, role: str, content: str) -> None:
        self._messages.append({"role": role, "content": content})  # type: ignore
        # trim oldest messages if we exceed the window
        if len(self._messages) > self._max_messages:
            self._messages = self._messages[-self._max_messages:]

    def get(self) -> list[ChatCompletionMessageParam]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages = []

    def __len__(self) -> int:
        return len(self._messages)

    def __repr__(self) -> str:
        return f"InContextMemory(messages={len(self)}, max={self._max_messages})"