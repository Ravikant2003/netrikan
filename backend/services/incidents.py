from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from services.notifiers import NotificationTargets, get_notifier
from utils.logger import get_logger

logger = get_logger("Incidents")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Incident:
    session_id: str
    user_id: Optional[str] = None
    created_at: datetime = field(default_factory=_utcnow)
    last_update_at: datetime = field(default_factory=_utcnow)
    status: str = "open"  # open|acknowledged|closed
    escalation_scheduled: bool = False
    escalation_task_id: Optional[str] = None
    last_payload: Dict[str, Any] = field(default_factory=dict)
    last_decision: Dict[str, Any] = field(default_factory=dict)


class IncidentManager:
    """
    Minimal incident state + delayed escalation (PRD: auto-escalate at T+90s if no response).
    Uses in-memory storage; can be replaced with Redis/Postgres later.
    """

    def __init__(self):
        self._incidents: Dict[str, Incident] = {}
        self._tasks: Dict[str, asyncio.Task] = {}
        self._notifier = get_notifier()

    def get_or_create(self, session_id: str, user_id: Optional[str] = None) -> Incident:
        inc = self._incidents.get(session_id)
        if inc is None:
            inc = Incident(session_id=session_id, user_id=user_id)
            self._incidents[session_id] = inc
        if user_id:
            inc.user_id = user_id
        return inc

    def ack(self, session_id: str) -> bool:
        inc = self._incidents.get(session_id)
        if not inc:
            return False
        inc.status = "acknowledged"
        inc.last_update_at = _utcnow()

        task_id = inc.escalation_task_id
        if task_id and task_id in self._tasks:
            self._tasks[task_id].cancel()
            self._tasks.pop(task_id, None)
        inc.escalation_task_id = None
        inc.escalation_scheduled = False
        return True

    def snapshot(self, session_id: str) -> Optional[Dict[str, Any]]:
        inc = self._incidents.get(session_id)
        if not inc:
            return None
        return {
            "session_id": inc.session_id,
            "status": inc.status,
            "created_at": inc.created_at.isoformat(),
            "last_update_at": inc.last_update_at.isoformat(),
            "escalation_scheduled": inc.escalation_scheduled,
        }

    def update_from_analysis(
        self,
        session_id: str,
        user_id: Optional[str],
        payload: Dict[str, Any],
        decision: Dict[str, Any],
        safety_index: Dict[str, Any],
    ) -> Dict[str, Any]:
        inc = self.get_or_create(session_id, user_id=user_id)
        inc.last_update_at = _utcnow()
        inc.last_payload = payload
        inc.last_decision = decision

        # Decide whether to schedule delayed escalation.
        # PRD behavior: notify guardians quickly, police escalation after ~90s if no acknowledgment.
        if inc.status != "open":
            return decision

        decision_name = str(decision.get("decision", "") or "")
        if decision_name != "EMERGENCY_ESCALATION":
            return decision

        emergency = (safety_index.get("emergency_anomaly") or {}) if isinstance(safety_index, dict) else {}
        level = str(emergency.get("level", "NONE") or "NONE").upper()
        weighted = float(decision.get("weighted_risk_score", 0.0) or 0.0)

        police_immediate = level == "CRITICAL" or weighted >= 0.95
        if police_immediate:
            return decision

        # If police isn't immediate, we schedule it and strip it from the immediate action list.
        actions = list(decision.get("required_actions", []) or [])
        if "POLICE_NOTIFICATION" in actions:
            actions = [a for a in actions if a != "POLICE_NOTIFICATION"]

        if not inc.escalation_scheduled:
            task_id = f"{session_id}:{int(datetime.now().timestamp())}"
            inc.escalation_scheduled = True
            inc.escalation_task_id = task_id
            self._tasks[task_id] = asyncio.create_task(self._auto_escalate_police(task_id, session_id))

        return {**decision, "required_actions": actions, "auto_escalation": {"police_after_s": 90}}

    async def _auto_escalate_police(self, task_id: str, session_id: str) -> None:
        try:
            await asyncio.sleep(90)
            inc = self._incidents.get(session_id)
            if not inc or inc.status != "open":
                return

            payload = inc.last_payload or {}
            decision = inc.last_decision or {}
            guardians = payload.get("guardians") or []
            targets = NotificationTargets(guardians=guardians, user_id=inc.user_id)

            # Notify guardians again
            for phone in targets.active_guardian_phones():
                await self._notifier.send_sms(phone, "AUTO-ESCALATION: No response detected. Escalating to police.")

            # Notify police via notifier
            await self._notifier.notify_police(
                {
                    "session_id": session_id,
                    "user_id": inc.user_id,
                    "last_location": {"lat": payload.get("latitude"), "lon": payload.get("longitude")},
                    "decision": decision,
                }
            )
            logger.critical(f"Auto-escalated to police for session={session_id}")
        except asyncio.CancelledError:
            return
        except Exception as e:
            logger.error(f"Auto escalation failed for {session_id}: {e}")
        finally:
            inc = self._incidents.get(session_id)
            if inc and inc.escalation_task_id == task_id:
                inc.escalation_task_id = None
                inc.escalation_scheduled = False
            self._tasks.pop(task_id, None)


incident_manager = IncidentManager()

