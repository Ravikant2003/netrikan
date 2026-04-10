from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol

import httpx

from utils.logger import get_logger

logger = get_logger("Notifiers")


class Notifier(Protocol):
    async def send_push(self, user_id: Optional[str], title: str, body: str, data: Optional[Dict[str, Any]] = None) -> None: ...
    async def send_sms(self, to_phone: str, message: str) -> None: ...
    async def make_call(self, to_phone: str, message: str) -> None: ...
    async def notify_police(self, payload: Dict[str, Any]) -> None: ...


def _env_truthy(name: str) -> bool:
    return os.environ.get(name, "").strip() in {"1", "true", "TRUE", "yes", "YES"}


@dataclass(frozen=True)
class NotificationTargets:
    guardians: List[Dict[str, Any]]
    user_id: Optional[str] = None

    def active_guardian_phones(self) -> List[str]:
        phones: List[str] = []
        for g in self.guardians or []:
            try:
                if g.get("active") is False:
                    continue
                phone = str(g.get("phone") or "").strip()
                if phone:
                    phones.append(phone)
            except Exception:
                continue
        return phones


class MockNotifier:
    async def send_push(self, user_id: Optional[str], title: str, body: str, data: Optional[Dict[str, Any]] = None) -> None:
        logger.warning(f"[MOCK][PUSH] user_id={user_id} title={title} body={body} data={data}")

    async def send_sms(self, to_phone: str, message: str) -> None:
        logger.warning(f"[MOCK][SMS] to={to_phone} message={message}")

    async def make_call(self, to_phone: str, message: str) -> None:
        logger.warning(f"[MOCK][CALL] to={to_phone} message={message}")

    async def notify_police(self, payload: Dict[str, Any]) -> None:
        logger.critical(f"[MOCK][POLICE] payload={payload}")


class WebhookNotifier(MockNotifier):
    """
    Minimal integration surface you can plug into Twilio/FCM/Police later.
    If you set these env vars, we POST JSON to your server:
      - NETRIKAN_PUSH_WEBHOOK_URL
      - NETRIKAN_SMS_WEBHOOK_URL
      - NETRIKAN_CALL_WEBHOOK_URL
      - NETRIKAN_POLICE_WEBHOOK_URL
    """

    def __init__(self):
        self.push_url = os.environ.get("NETRIKAN_PUSH_WEBHOOK_URL", "").strip() or None
        self.sms_url = os.environ.get("NETRIKAN_SMS_WEBHOOK_URL", "").strip() or None
        self.call_url = os.environ.get("NETRIKAN_CALL_WEBHOOK_URL", "").strip() or None
        self.police_url = os.environ.get("NETRIKAN_POLICE_WEBHOOK_URL", "").strip() or None

    async def _post(self, url: str, payload: Dict[str, Any]) -> None:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code >= 300:
                    logger.warning(f"Webhook {url} returned {resp.status_code}: {resp.text[:300]}")
        except Exception as e:
            logger.warning(f"Webhook post failed ({url}): {e}")

    async def send_push(self, user_id: Optional[str], title: str, body: str, data: Optional[Dict[str, Any]] = None) -> None:
        if not self.push_url:
            return await super().send_push(user_id, title, body, data)
        await self._post(self.push_url, {"user_id": user_id, "title": title, "body": body, "data": data or {}})

    async def send_sms(self, to_phone: str, message: str) -> None:
        if not self.sms_url:
            return await super().send_sms(to_phone, message)
        await self._post(self.sms_url, {"to": to_phone, "message": message})

    async def make_call(self, to_phone: str, message: str) -> None:
        if not self.call_url:
            return await super().make_call(to_phone, message)
        await self._post(self.call_url, {"to": to_phone, "message": message})

    async def notify_police(self, payload: Dict[str, Any]) -> None:
        if not self.police_url:
            return await super().notify_police(payload)
        await self._post(self.police_url, payload)


def get_notifier() -> Notifier:
    """
    Default: webhook-capable mock (logs if no webhook env vars are set).
    """
    if _env_truthy("NETRIKAN_NOTIFIER_MOCK_ONLY"):
        return MockNotifier()
    return WebhookNotifier()

