from __future__ import annotations

from collections import defaultdict


class SessionStore:
    def __init__(self, max_messages: int = 20) -> None:
        self.max_messages = max_messages
        self._messages: dict[str, list[dict[str, str]]] = defaultdict(list)

    def append(self, session_id: str, role: str, content: str) -> None:
        history = self._messages[session_id]
        history.append({"role": role, "content": content})
        del history[:-self.max_messages]

    def get(self, session_id: str) -> list[dict[str, str]]:
        return list(self._messages[session_id])


sessions = SessionStore()
