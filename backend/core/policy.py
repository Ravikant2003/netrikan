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


def apply_action_policy(
    orchestrator_decision: Dict[str, Any],
    processed_data: Dict[str, Any],
    safety_index: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Safety guardrails for tool/action execution.

    This does NOT decide the "decision" label; it only filters `required_actions`
    and returns an audit payload you can surface in a simulation.
    """
    required_actions = list(orchestrator_decision.get("required_actions", []) or [])
    allowed: List[str] = []
    blocked: Dict[str, str] = {}

    text_signal = str(processed_data.get("text_signal", "") or "")
    has_distress = _has_distress(text_signal)
    injection_like = _looks_like_prompt_injection(text_signal)

    weighted_risk = float(orchestrator_decision.get("weighted_risk_score", 0.0) or 0.0)
    combined_risk = float(safety_index.get("combined_risk_score", 0.0) or 0.0)
    emergency = safety_index.get("emergency_anomaly", {}) or {}
    emergency_level = str(emergency.get("level", "NONE") or "NONE").upper()

    for action in required_actions:
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

        if action == "SMS_GUARDIANS":
            if emergency_level in {"CRITICAL", "ELEVATED"} or weighted_risk >= 0.7 or has_distress:
                allowed.append(action)
            else:
                blocked[action] = "No strong emergency indicators; guardian SMS suppressed."
            continue

        if action == "POLICE_NOTIFICATION":
            # Hard guardrail: never allow "prompt injection" style text to be the sole trigger.
            if injection_like and not has_distress:
                blocked[action] = "Prompt-injection-like text without distress; police notification blocked."
                continue

            if emergency_level == "CRITICAL" or (has_distress and max(weighted_risk, combined_risk) >= 0.7):
                allowed.append(action)
            else:
                blocked[action] = "Police notification requires CRITICAL emergency or distress + high risk."
            continue

        # Unknown actions: allow but log (keeps forward compatibility)
        logger.warning(f"Unknown action '{action}' passed through policy allow-list.")
        allowed.append(action)

    audit = {
        "allowed_actions": allowed,
        "blocked_actions": blocked,
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

