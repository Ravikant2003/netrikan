from __future__ import annotations

from typing import Any, Dict, List, Tuple

from utils.logger import get_logger

logger = get_logger("SafetyPolicy")


_DISTRESS_TERMS = {"help", "save me", "emergency", "danger", "unsafe", "sos", "attack", "kidnap", "rape"}
_INJECTION_TERMS = {
    "ignore previous",
    "ignore instructions",
    "system prompt",
    "developer message",
    "jailbreak",
    "bypass",
}


def _has_distress(text: str) -> bool:
    t = (text or "").lower()
    return any(term in t for term in _DISTRESS_TERMS)


def _looks_like_prompt_injection(text: str) -> bool:
    t = (text or "").lower()
    return any(term in t for term in _INJECTION_TERMS)


def _get_notification_level(processed_data: Dict[str, Any]) -> str:
    """Get notification level from processed data or default to 'low'."""
    level = str(processed_data.get("notification_level", "") or "").lower()
    if level in {"high", "medium", "low"}:
        return level
    return "low"


def apply_action_policy(
    orchestrator_decision: Dict[str, Any],
    processed_data: Dict[str, Any],
    safety_index: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Safety guardrails for tool/action execution.

    This does NOT decide the "decision" label; it only filters `required_actions`
    and returns an audit payload you can surface in a simulation.
    
    Notification Levels:
    - LOW (Safe): No actions triggered
    - MEDIUM (Human in the Loop): Telegram notification only, requires human confirmation
    - HIGH (Automatic): All notifications (Telegram, Phone, Email) triggered automatically
    """
    required_actions = list(orchestrator_decision.get("required_actions", []) or [])
    allowed: List[str] = []
    blocked: Dict[str, str] = {}

    text_signal = str(processed_data.get("text_signal", "") or "")
    has_distress = _has_distress(text_signal)
    injection_like = _looks_like_prompt_injection(text_signal)
    notification_level = _get_notification_level(processed_data)

    weighted_risk = float(orchestrator_decision.get("weighted_risk_score", 0.0) or 0.0)
    combined_risk = float(safety_index.get("combined_risk_score", 0.0) or 0.0)
    emergency = safety_index.get("emergency_anomaly", {}) or {}
    emergency_level = str(emergency.get("level", "NONE") or "NONE").upper()

    decision = str(orchestrator_decision.get("decision", "") or "")

    for action in required_actions:
        # Always allow push notifications (for all levels)
        if action == "PUSH_NOTIFICATION":
            allowed.append(action)
            continue

        if action == "MAP_REROUTING":
            dest = processed_data.get("destination") or {}
            if "lat" in dest and "lon" in dest:
                allowed.append(action)
            else:
                blocked[action] = "Destination missing; cannot compute reroute."
            continue

        if action == "SAFE_PLACES_SUGGESTION":
            allowed.append(action)
            continue

        # TELEGRAM_NOTIFY - For MEDIUM and HIGH levels
        if action == "TELEGRAM_NOTIFY":
            # Allow if decision is ROUTE_ADJUSTMENT (medium) or EMERGENCY_ESCALATION (high)
            if decision in {"ROUTE_ADJUSTMENT", "EMERGENCY_ESCALATION"}:
                allowed.append(action)
            else:
                blocked[action] = "Telegram notification only for MEDIUM/HIGH risk levels."
            continue

        # SMS_GUARDIANS - Only for MEDIUM and HIGH levels
        if action == "SMS_GUARDIANS":
            if decision in {"ROUTE_ADJUSTMENT", "EMERGENCY_ESCALATION"} or emergency_level in {"CRITICAL", "ELEVATED"} or weighted_risk >= 0.7 or has_distress:
                allowed.append(action)
            else:
                blocked[action] = "SMS only for MEDIUM/HIGH risk levels or strong emergency indicators."
            continue

        # ADB_CALL - Only for HIGH level (automatic phone call)
        if action == "ADB_CALL":
            if decision == "EMERGENCY_ESCALATION":
                allowed.append(action)
            else:
                blocked[action] = "Phone call only for HIGH risk level (EMERGENCY_ESCALATION)."
            continue

        # EMAIL_GUARDIANS - Only for HIGH level
        if action == "EMAIL_GUARDIANS":
            if decision == "EMERGENCY_ESCALATION":
                allowed.append(action)
            else:
                blocked[action] = "Email only for HIGH risk level (EMERGENCY_ESCALATION)."
            continue

        # POLICE_NOTIFICATION - Only for HIGH level
        if action == "POLICE_NOTIFICATION":
            # Hard guardrail: never allow "prompt injection" style text to be the sole trigger.
            if injection_like and not has_distress:
                blocked[action] = "Prompt-injection-like text without distress; police notification blocked."
                continue

            if decision == "EMERGENCY_ESCALATION":
                if has_distress or emergency_level == "CRITICAL" or max(weighted_risk, combined_risk) >= 0.7:
                    allowed.append(action)
                else:
                    blocked[action] = "Police notification requires distress or CRITICAL emergency."
            else:
                blocked[action] = "Police notification only for HIGH risk level (EMERGENCY_ESCALATION)."
            continue

        # Unknown actions: allow but log (keeps forward compatibility)
        logger.warning(f"Unknown action '{action}' passed through policy allow-list.")
        allowed.append(action)

    audit = {
        "allowed_actions": allowed,
        "blocked_actions": blocked,
        "notification_level": notification_level,
        "signals": {
            "has_distress_text": has_distress,
            "prompt_injection_suspected": injection_like,
            "emergency_level": emergency_level,
            "weighted_risk_score": round(float(weighted_risk), 4),
            "combined_risk_score": round(float(combined_risk), 4),
        },
    }

    return {
        **orchestrator_decision,
        "required_actions": allowed,
        "policy": audit,
    }

