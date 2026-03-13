from __future__ import annotations

from collections import deque
from threading import Lock
from typing import Deque, Dict, List, Optional
from uuid import uuid4

from agentic.models import MemoryEvent
from config import settings


class SessionMemory:
    def __init__(self, session_id: str, max_events: int = 12):
        self.session_id = session_id
        self._events: Deque[MemoryEvent] = deque(maxlen=max_events)

    def add_event(self, kind: str, payload: Dict[str, object]) -> None:
        self._events.append(MemoryEvent(kind=kind, payload=dict(payload)))

    def to_list(self) -> List[Dict[str, object]]:
        return [
            {"kind": event.kind, "payload": event.payload}
            for event in self._events
        ]

    @property
    def size(self) -> int:
        return len(self._events)


class MemoryStore:
    def __init__(self, max_events: int = 12):
        self.max_events = max_events
        self._sessions: Dict[str, SessionMemory] = {}
        self._lock = Lock()

    def get_session(self, session_id: Optional[str] = None) -> SessionMemory:
        resolved_session_id = session_id or str(uuid4())
        with self._lock:
            if resolved_session_id not in self._sessions:
                self._sessions[resolved_session_id] = SessionMemory(
                    session_id=resolved_session_id,
                    max_events=self.max_events,
                )
            return self._sessions[resolved_session_id]


memory_store = MemoryStore(max_events=settings.AGENT_MEMORY_WINDOW)
