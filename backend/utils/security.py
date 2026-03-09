from collections import defaultdict, deque
from time import time
from typing import Deque, DefaultDict, Optional
from uuid import uuid4

from fastapi import Header, HTTPException, Request, status
from config import settings

REQUEST_WINDOW_SECONDS = 60
_request_buckets: DefaultDict[str, Deque[float]] = defaultdict(deque)
_active_sessions: dict[str, str] = {}


def create_session_token(username: str) -> str:
    token = str(uuid4())
    _active_sessions[token] = username
    return token


def verify_session_token(
    x_auth_token: Optional[str] = Header(default=None, alias="X-Auth-Token"),
) -> str:
    if not x_auth_token or x_auth_token not in _active_sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing auth token",
        )
    return _active_sessions[x_auth_token]


def revoke_session_token(
    x_auth_token: Optional[str] = Header(default=None, alias="X-Auth-Token"),
) -> str:
    if not x_auth_token or x_auth_token not in _active_sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing auth token",
        )
    return _active_sessions.pop(x_auth_token)


def rate_limit(request: Request) -> None:
    limit = max(1, settings.RATE_LIMIT_PER_MINUTE)
    client_host = request.client.host if request.client else "unknown"

    timestamps = _request_buckets[client_host]
    now = time()

    while timestamps and now - timestamps[0] > REQUEST_WINDOW_SECONDS:
        timestamps.popleft()

    if len(timestamps) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )

    timestamps.append(now)
