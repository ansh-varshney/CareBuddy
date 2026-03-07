"""Conversation memory management — Redis if available, in-memory fallback otherwise."""

import json
import logging
from collections import defaultdict

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

MESSAGE_TYPES = {
    "human": HumanMessage,
    "ai": AIMessage,
    "system": SystemMessage,
}


class InMemoryStore:
    """Simple in-process conversation store (dev fallback when Redis is unavailable)."""

    def __init__(self):
        self._store: dict[str, list] = defaultdict(list)

    async def rpush(self, key: str, value: str):
        self._store[key].append(value)

    async def ltrim(self, key: str, start: int, end: int):
        items = self._store[key]
        if end == -1:
            end = len(items)
        elif end < 0:
            end = max(0, len(items) + end + 1)
        self._store[key] = items[max(0, start):end]

    async def lrange(self, key: str, start: int, end: int) -> list:
        items = self._store[key]
        if end == -1:
            return items[start:]
        return items[start: end + 1]

    async def delete(self, key: str):
        self._store.pop(key, None)

    async def close(self):
        pass


class ConversationMemory:
    """
    Conversation memory with Redis backend and in-memory fallback.

    Falls back to in-process dict if Redis is not running.
    """

    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self._backend = InMemoryStore()

    async def _get_backend(self):
        """Return the already-initialized backend."""
        return self._backend

    def _key(self, conversation_id: str) -> str:
        return f"carebuddy:memory:{conversation_id}"

    async def add_message(self, conversation_id: str, role: str, content: str) -> None:
        backend = await self._get_backend()
        message = json.dumps({"role": role, "content": content})
        await backend.rpush(self._key(conversation_id), message)
        await backend.ltrim(self._key(conversation_id), -self.max_history, -1)

    async def get_messages(self, conversation_id: str) -> list:
        backend = await self._get_backend()
        raw_messages = await backend.lrange(self._key(conversation_id), 0, -1)
        messages = []
        for raw in raw_messages:
            data = json.loads(raw)
            msg_class = MESSAGE_TYPES.get(data["role"], HumanMessage)
            messages.append(msg_class(content=data["content"]))
        return messages

    async def get_messages_as_text(self, conversation_id: str) -> str:
        backend = await self._get_backend()
        raw_messages = await backend.lrange(self._key(conversation_id), 0, -1)
        labels = {"human": "User", "ai": "Assistant", "system": "System"}
        lines = []
        for raw in raw_messages:
            data = json.loads(raw)
            label = labels.get(data["role"], data["role"])
            lines.append(f"{label}: {data['content']}")
        return "\n".join(lines)

    async def clear(self, conversation_id: str) -> None:
        backend = await self._get_backend()
        await backend.delete(self._key(conversation_id))

    async def close(self) -> None:
        if self._backend:
            await self._backend.close()


# Global memory instance
memory = ConversationMemory()

