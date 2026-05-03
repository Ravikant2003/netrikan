from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol

import httpx

from utils.logger import get_logger

logger = get_logger("Notifiers")

_fcm_app = None


def _get_fcm_app():
    global _fcm_app
    if _fcm_app is not None:
        return _fcm_app
    try:
        import firebase_admin
        from firebase_admin import credentials
    except Exception as exc:
        raise RuntimeError("firebase-admin is not installed. Add it to requirements.txt") from exc

    if not firebase_admin._apps:
        cred = credentials.ApplicationDefault()
        _fcm_app = firebase_admin.initialize_app(cred)
    else:
        _fcm_app = firebase_admin.get_app()
    return _fcm_app


class Notifier(Protocol):
    async def send_push(self, user_id: Optional[str], title: str, body: str, data: Optional[Dict[str, Any]] = None) -> None: ...
    async def send_sms(self, to_phone: str, message: str) -> None: ...
    async def make_call(self, to_phone: str, message: str) -> None: ...
    async def send_email(self, to_email: str, subject: str, body: str) -> None: ...
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

    async def send_email(self, to_email: str, subject: str, body: str) -> None:
        logger.warning(f"[MOCK][EMAIL] to={to_email} subject={subject} body={body}")

    async def notify_police(self, payload: Dict[str, Any]) -> None:
        logger.critical(f"[MOCK][POLICE] payload={payload}")


class WebhookNotifier(MockNotifier):
    """
    Minimal integration surface you can plug into Twilio/FCM/Police later.
    If you set these env vars, we POST JSON to your server:
      - NETRIKAN_PUSH_WEBHOOK_URL
      - NETRIKAN_SMS_WEBHOOK_URL
      - NETRIKAN_CALL_WEBHOOK_URL
      - NETRIKAN_EMAIL_WEBHOOK_URL
      - NETRIKAN_POLICE_WEBHOOK_URL
    """

    def __init__(self):
        self.push_url = os.environ.get("NETRIKAN_PUSH_WEBHOOK_URL", "").strip() or None
        self.sms_url = os.environ.get("NETRIKAN_SMS_WEBHOOK_URL", "").strip() or None
        self.call_url = os.environ.get("NETRIKAN_CALL_WEBHOOK_URL", "").strip() or None
        self.email_url = os.environ.get("NETRIKAN_EMAIL_WEBHOOK_URL", "").strip() or None
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

    async def send_email(self, to_email: str, subject: str, body: str) -> None:
        if not self.email_url:
            return await super().send_email(to_email, subject, body)
        await self._post(self.email_url, {"to": to_email, "subject": subject, "body": body})

    async def notify_police(self, payload: Dict[str, Any]) -> None:
        if not self.police_url:
            return await super().notify_police(payload)
        await self._post(self.police_url, payload)


class FcmPushNotifier(MockNotifier):
    """
    Firebase Cloud Messaging push notifier.

    Required env vars:
      - FCM_PROJECT_ID (used in message metadata)
      - GOOGLE_APPLICATION_CREDENTIALS (service account JSON path)
    """

    def __init__(self, fallback: Optional[Notifier] = None):
        self.project_id = os.environ.get("FCM_PROJECT_ID", "").strip()
        if not self.project_id:
            raise ValueError("FCM_PROJECT_ID is required for FCM push")
        self._fallback = fallback

        # Initialize once; uses GOOGLE_APPLICATION_CREDENTIALS.
        _get_fcm_app()

    async def send_push(self, user_id: Optional[str], title: str, body: str, data: Optional[Dict[str, Any]] = None) -> None:
        if not user_id:
            if self._fallback:
                return await self._fallback.send_push(user_id, title, body, data)
            return await super().send_push(user_id, title, body, data)

        try:
            from firebase_admin import messaging
            from services.push_tokens import get_tokens

            tokens = get_tokens(user_id)
            if not tokens:
                logger.warning(f"No FCM tokens registered for user_id={user_id}")
                return
            logger.info(f"Sending FCM push to user_id={user_id} tokens={len(tokens)}")

            message = messaging.MulticastMessage(
                notification=messaging.Notification(title=title, body=body),
                data={k: str(v) for k, v in (data or {}).items()},
                tokens=tokens,
            )
            response = messaging.send_multicast(message)
            if response.failure_count:
                logger.warning(f"FCM failures: {response.failure_count} of {len(tokens)}")
        except Exception as exc:
            logger.warning(f"FCM send failed: {exc}")
            if self._fallback:
                return await self._fallback.send_push(user_id, title, body, data)

    async def send_sms(self, to_phone: str, message: str) -> None:
        if self._fallback:
            return await self._fallback.send_sms(to_phone, message)
        return await super().send_sms(to_phone, message)

    async def make_call(self, to_phone: str, message: str) -> None:
        if self._fallback:
            return await self._fallback.make_call(to_phone, message)
        return await super().make_call(to_phone, message)

    async def send_email(self, to_email: str, subject: str, body: str) -> None:
        if self._fallback:
            return await self._fallback.send_email(to_email, subject, body)
        return await super().send_email(to_email, subject, body)

    async def notify_police(self, payload: Dict[str, Any]) -> None:
        if self._fallback:
            return await self._fallback.notify_police(payload)
        return await super().notify_police(payload)


class TwilioWhatsAppNotifier(MockNotifier):
    """
    Twilio WhatsApp sender.

    Required env vars:
      - TWILIO_ACCOUNT_SID
      - TWILIO_AUTH_TOKEN
      - TWILIO_WHATSAPP_FROM  (e.g., whatsapp:+14155238886)

    Optional:
      - TWILIO_WHATSAPP_TEMPLATE_SID
      - TWILIO_WHATSAPP_TEMPLATE_VARS (JSON string)
            - TWILIO_WHATSAPP_POLICE_TO (when set, police alerts go to this WhatsApp number)
    """

    def __init__(self, fallback: Optional[Notifier] = None):
        self.account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "").strip()
        self.auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "").strip()
        self.whatsapp_from = os.environ.get("TWILIO_WHATSAPP_FROM", "").strip()
        self.template_sid = os.environ.get("TWILIO_WHATSAPP_TEMPLATE_SID", "").strip()
        self.template_vars = os.environ.get("TWILIO_WHATSAPP_TEMPLATE_VARS", "{}").strip()
        self.police_to = os.environ.get("TWILIO_WHATSAPP_POLICE_TO", "").strip()
        self._fallback = fallback

        if not self.account_sid or not self.auth_token or not self.whatsapp_from:
            raise ValueError("Twilio WhatsApp notifier requires TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM")

        try:
            from twilio.rest import Client
        except Exception as exc:
            raise RuntimeError("Twilio SDK is not installed. Add 'twilio' to requirements.txt") from exc

        self._client = Client(self.account_sid, self.auth_token)

    async def send_push(self, user_id: Optional[str], title: str, body: str, data: Optional[Dict[str, Any]] = None) -> None:
        if self._fallback:
            return await self._fallback.send_push(user_id, title, body, data)
        return await super().send_push(user_id, title, body, data)

    async def send_sms(self, to_phone: str, message: str) -> None:
        to_number = to_phone.strip()
        if not to_number.startswith("whatsapp:"):
            to_number = f"whatsapp:{to_number}"

        try:
            if self.template_sid:
                self._client.messages.create(
                    from_=self.whatsapp_from,
                    to=to_number,
                    content_sid=self.template_sid,
                    content_variables=self.template_vars,
                )
            else:
                self._client.messages.create(
                    from_=self.whatsapp_from,
                    to=to_number,
                    body=message,
                )
        except Exception as exc:
            logger.warning(f"Twilio WhatsApp send failed: {exc}")

    async def make_call(self, to_phone: str, message: str) -> None:
        if self._fallback:
            return await self._fallback.make_call(to_phone, message)
        return await super().make_call(to_phone, message)

    async def send_email(self, to_email: str, subject: str, body: str) -> None:
        if self._fallback:
            return await self._fallback.send_email(to_email, subject, body)
        return await super().send_email(to_email, subject, body)

    async def notify_police(self, payload: Dict[str, Any]) -> None:
        if self.police_to:
            try:
                session_id = payload.get("session_id", "unknown")
                last_location = payload.get("last_location") or {}
                decision = payload.get("decision") or {}
                lat = last_location.get("lat")
                lon = last_location.get("lon")
                decision_name = decision.get("decision", "UNKNOWN")
                message = (
                    "POLICE ALERT (SIM): "
                    f"session={session_id}, decision={decision_name}, "
                    f"location=({lat}, {lon})"
                )
                await self.send_sms(self.police_to, message)
                return
            except Exception as exc:
                logger.warning(f"Twilio WhatsApp police alert failed: {exc}")

        if self._fallback:
            return await self._fallback.notify_police(payload)
        return await super().notify_police(payload)


def get_notifier() -> Notifier:
    """
    Default: webhook-capable mock (logs if no webhook env vars are set).
    """
    if _env_truthy("NETRIKAN_NOTIFIER_MOCK_ONLY"):
        return MockNotifier()
    webhook = WebhookNotifier()
    notifier: Notifier = webhook

    # Prefer FCM for push if configured.
    if os.environ.get("FCM_PROJECT_ID") and os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        try:
            notifier = FcmPushNotifier(fallback=notifier)
        except Exception as exc:
            logger.warning(f"FCM notifier unavailable: {exc}")

    # Prefer Twilio WhatsApp for SMS if configured.
    if os.environ.get("TWILIO_ACCOUNT_SID") and os.environ.get("TWILIO_AUTH_TOKEN") and os.environ.get("TWILIO_WHATSAPP_FROM"):
        try:
            notifier = TwilioWhatsAppNotifier(fallback=notifier)
        except Exception as exc:
            logger.warning(f"Twilio WhatsApp notifier unavailable: {exc}")

    return notifier

