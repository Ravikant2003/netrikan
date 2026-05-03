from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PushTokenStore:
    tokens_by_user: Dict[str, List[str]] = field(default_factory=dict)

    def register(self, user_id: str, token: str) -> int:
        token = token.strip()
        if not token:
            return 0
        tokens = self.tokens_by_user.setdefault(user_id, [])
        if token not in tokens:
            tokens.append(token)
        return len(tokens)

    def get_tokens(self, user_id: str) -> List[str]:
        return list(self.tokens_by_user.get(user_id, []))

    def remove_token(self, user_id: str, token: str) -> None:
        tokens = self.tokens_by_user.get(user_id)
        if not tokens:
            return
        try:
            tokens.remove(token)
        except ValueError:
            return
        if not tokens:
            self.tokens_by_user.pop(user_id, None)


store = PushTokenStore()


def register_token(user_id: str, token: str) -> int:
    return store.register(user_id, token)


def get_tokens(user_id: str) -> List[str]:
    return store.get_tokens(user_id)
