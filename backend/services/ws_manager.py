from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, Set

from fastapi import WebSocket

from utils.logger import get_logger

logger = get_logger("WS")


@dataclass
class _Room:
    sockets: Set[WebSocket] = field(default_factory=set)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


class WebSocketManager:
    def __init__(self):
        self._rooms: Dict[str, _Room] = {}

    def _room(self, room_id: str) -> _Room:
        if room_id not in self._rooms:
            self._rooms[room_id] = _Room()
        return self._rooms[room_id]

    async def connect(self, room_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        room = self._room(room_id)
        async with room.lock:
            room.sockets.add(websocket)

    async def disconnect(self, room_id: str, websocket: WebSocket) -> None:
        room = self._rooms.get(room_id)
        if not room:
            return
        async with room.lock:
            room.sockets.discard(websocket)

    async def broadcast(self, room_id: str, message: Dict[str, Any]) -> None:
        room = self._rooms.get(room_id)
        if not room:
            return
        async with room.lock:
            sockets = list(room.sockets)
        dead: list[WebSocket] = []
        for ws in sockets:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        if dead:
            async with room.lock:
                for ws in dead:
                    room.sockets.discard(ws)


ws_manager = WebSocketManager()

