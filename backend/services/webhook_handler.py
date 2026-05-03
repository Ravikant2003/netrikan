"""
Webhook service for external integrations (n8n, Zapier, custom server)
"""
import os
import httpx
from typing import Dict, Any, List, Optional
from utils.logger import get_logger

logger = get_logger("WebhookHandler")


class WebhookHandler:
    """
    Sends notifications to external webhook URLs.
    Use with n8n/Zapier to handle SMS, calls, emails for free.
    """
    
    def __init__(self):
        self.push_url = os.environ.get("NETRIKAN_PUSH_WEBHOOK_URL", "").strip() or None
        self.sms_url = os.environ.get("NETRIKAN_SMS_WEBHOOK_URL", "").strip() or None
        self.call_url = os.environ.get("NETRIKAN_CALL_WEBHOOK_URL", "").strip() or None
        self.police_url = os.environ.get("NETRIKAN_POLICE_WEBHOOK_URL", "").strip() or None
    
    def is_configured(self) -> bool:
        """Check if any webhook is configured."""
        return any([self.push_url, self.sms_url, self.call_url, self.police_url])
    
    async def send_push(self, user_id: str, title: str, body: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send push notification via webhook."""
        if not self.push_url:
            return {"status": "not_configured", "reason": "NETRIKAN_PUSH_WEBHOOK_URL not set"}
        
        payload = {
            "type": "push",
            "user_id": user_id,
            "title": title,
            "body": body,
            "data": data or {},
            "source": "netrikan"
        }
        
        return await self._send(self.push_url, payload)
    
    async def send_sms(self, to_phone: str, message: str) -> Dict[str, Any]:
        """Send SMS via webhook."""
        if not self.sms_url:
            return {"status": "not_configured", "reason": "NETRIKAN_SMS_WEBHOOK_URL not set"}
        
        payload = {
            "type": "sms",
            "to": to_phone,
            "message": message,
            "source": "netrikan"
        }
        
        return await self._send(self.sms_url, payload)
    
    async def send_call(self, to_phone: str, message: str) -> Dict[str, Any]:
        """Send voice call via webhook."""
        if not self.call_url:
            return {"status": "not_configured", "reason": "NETRIKAN_CALL_WEBHOOK_URL not set"}
        
        payload = {
            "type": "call",
            "to": to_phone,
            "message": message,
            "source": "netrikan"
        }
        
        return await self._send(self.call_url, payload)
    
    async def send_police_alert(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send police/emergency alert via webhook."""
        if not self.police_url:
            return {"status": "not_configured", "reason": "NETRIKAN_POLICE_WEBHOOK_URL not set"}
        
        full_payload = {
            "type": "police_alert",
            "source": "netrikan",
            **payload
        }
        
        return await self._send(self.police_url, full_payload)
    
    async def _send(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send webhook POST request."""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code >= 200 and response.status_code < 300:
                    logger.info(f"Webhook sent successfully to {url}")
                    return {
                        "status": "success",
                        "url": url,
                        "response_code": response.status_code
                    }
                else:
                    logger.warning(f"Webhook returned {response.status_code}: {response.text[:200]}")
                    return {
                        "status": "failed",
                        "url": url,
                        "response_code": response.status_code,
                        "error": response.text[:200]
                    }
        except Exception as e:
            logger.error(f"Webhook send failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


# Singleton instance
_webhook_handler: Optional[WebhookHandler] = None


def get_webhook_handler() -> WebhookHandler:
    global _webhook_handler
    if _webhook_handler is None:
        _webhook_handler = WebhookHandler()
    return _webhook_handler


def is_webhook_configured() -> bool:
    """Check if any webhook is configured."""
    handler = get_webhook_handler()
    return handler.is_configured()