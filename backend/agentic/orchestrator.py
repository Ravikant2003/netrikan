from __future__ import annotations

from typing import Any, Dict, List

from agentic.memory import memory_store
from agentic.models import AgentRunSummary
from agentic.planner import build_planner
from agentic.tools import build_default_registry
from config import settings


class AgenticSafetyOrchestrator:
    def __init__(self) -> None:
        self.registry = build_default_registry()
        self.planner = build_planner()

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        session = memory_store.get_session(payload.get("session_id"))
        normalized_context = self._normalize_context(payload)
        tool_trace: List[Dict[str, Any]] = []
        tool_outputs: Dict[str, Dict[str, Any]] = {}

        session.add_event("request", normalized_context)

        for _ in range(settings.AGENT_MAX_STEPS):
            next_action = self.planner.next_action(
                context=normalized_context,
                tool_trace=tool_trace,
                available_tools=self.registry.definitions(),
            )
            if next_action.done or not next_action.tool_name:
                break

            result = self.registry.execute(
                tool_name=next_action.tool_name,
                arguments=next_action.arguments,
                context=normalized_context,
            )
            tool_outputs[result.tool_name] = result.output
            trace_entry = {
                "tool_name": result.tool_name,
                "arguments": next_action.arguments,
                "rationale": next_action.rationale or result.rationale,
                "latency_ms": result.latency_ms,
                "output": result.output,
            }
            tool_trace.append(trace_entry)
            session.add_event("tool", trace_entry)

        summary = self._synthesize(
            session_id=session.session_id,
            context=normalized_context,
            tool_outputs=tool_outputs,
            tool_trace=tool_trace,
            planner_mode=getattr(self.planner, "mode", "heuristic"),
            memory_size=session.size,
        )
        session.add_event(
            "summary",
            {
                "decision": summary.decision,
                "confidence": summary.confidence,
                "reasons": summary.reasons,
            },
        )
        return {
            "session_id": summary.session_id,
            "decision": summary.decision,
            "reasons": summary.reasons,
            "safety": summary.safety,
            "route": summary.route,
            "emergency": summary.emergency,
            "confidence": summary.confidence,
            "tool_trace": summary.tool_trace,
            "agent_summary": summary.agent_summary,
            "tools_used": summary.tools_used,
            "planner_mode": summary.planner_mode,
            "memory_size": summary.memory_size,
        }

    @staticmethod
    def _normalize_context(payload: Dict[str, Any]) -> Dict[str, Any]:
        destination = payload.get("destination") or {}
        return {
            "latitude": float(payload.get("latitude", 0.0)),
            "longitude": float(payload.get("longitude", 0.0)),
            "destination": {
                "lat": float(destination.get("lat", payload.get("latitude", 0.0))),
                "lon": float(destination.get("lon", payload.get("longitude", 0.0))),
            } if destination else {},
            "time_of_day": payload.get("time_of_day", "day"),
            "speed": float(payload.get("speed", 0.0)),
            "route_deviation": bool(payload.get("route_deviation", False)),
            "text_signal": payload.get("text_signal", ""),
            "severity": payload.get("severity", "low"),
            "session_id": payload.get("session_id"),
            "user_id": payload.get("user_id"),
        }

    def _synthesize(
        self,
        *,
        session_id: str,
        context: Dict[str, Any],
        tool_outputs: Dict[str, Dict[str, Any]],
        tool_trace: List[Dict[str, Any]],
        planner_mode: str,
        memory_size: int,
    ) -> AgentRunSummary:
        crime_result = tool_outputs.get("crime_risk_lookup", {})
        ml_result = tool_outputs.get("ml_risk_prediction", {})
        route_result = tool_outputs.get("route_safety_analysis", {})
        emergency_result = tool_outputs.get("emergency_signal_assessment", {})

        crime_score_value = float(crime_result.get("crime_score", 0.0))
        ml_risk_value = float(ml_result.get("predicted_risk", crime_score_value))
        route_risk_value = float(route_result.get("route_risk", 0.0))
        anomaly_score = float(emergency_result.get("anomaly_score", 0.0))

        weighted_risk = (
            0.55 * ml_risk_value
            + 0.25 * crime_score_value
            + 0.20 * route_risk_value
        )
        if emergency_result.get("level") == "CRITICAL":
            weighted_risk = min(1.0, weighted_risk + 0.25)
        elif emergency_result.get("level") == "ELEVATED":
            weighted_risk = min(1.0, weighted_risk + 0.10)

        risk_level = self._risk_level(weighted_risk)
        route_details = {
            "distance_km": round(float(route_result.get("distance_km", 0.5)), 2),
            "eta_minutes": int(route_result.get("eta_minutes", 3)),
            "risk_weight": round(route_risk_value, 4),
        }
        route_payload = {
            "recommended_route": route_result.get("recommended_route", "current_route"),
            "route_risk": round(route_risk_value, 4),
            "details": route_details,
        }

        safety_payload = {
            "risk_score": round(weighted_risk, 4),
            "risk_level": risk_level,
            "explanation": self._build_safety_explanation(
                weighted_risk=weighted_risk,
                ml_risk=ml_risk_value,
                crime_risk=crime_score_value,
                route_risk=route_risk_value,
            ),
        }

        emergency_payload = {
            "level": emergency_result.get("level", "NONE"),
            "message": emergency_result.get("message", "No immediate emergency indicators detected."),
        }

        decision, reasons = self._build_decision(
            safety_payload=safety_payload,
            route_payload=route_payload,
            emergency_payload=emergency_payload,
            anomaly_score=anomaly_score,
        )
        confidence = self._estimate_confidence(tool_outputs)
        agent_summary = self._build_agent_summary(
            decision=decision,
            reasons=reasons,
            safety_payload=safety_payload,
            route_payload=route_payload,
            emergency_payload=emergency_payload,
            context=context,
        )

        return AgentRunSummary(
            session_id=session_id,
            decision=decision,
            reasons=reasons,
            safety=safety_payload,
            route=route_payload,
            emergency=emergency_payload,
            confidence=confidence,
            tool_trace=tool_trace,
            agent_summary=agent_summary,
            tools_used=[step["tool_name"] for step in tool_trace],
            planner_mode=planner_mode,
            memory_size=memory_size,
        )

    @staticmethod
    def _risk_level(risk_score: float) -> str:
        if risk_score >= 0.7:
            return "UNSAFE"
        if risk_score >= 0.35:
            return "MODERATE"
        return "SAFE"

    @staticmethod
    def _estimate_confidence(tool_outputs: Dict[str, Dict[str, Any]]) -> float:
        expected_tools = 4
        coverage = min(1.0, len(tool_outputs) / expected_tools)
        return round(0.6 + 0.35 * coverage, 4)

    @staticmethod
    def _build_safety_explanation(
        *,
        weighted_risk: float,
        ml_risk: float,
        crime_risk: float,
        route_risk: float,
    ) -> str:
        return (
            "Ensemble safety assessment combining XGBoost prediction, local crime exposure, "
            f"and route risk. Final risk={weighted_risk:.2f} (ml={ml_risk:.2f}, crime={crime_risk:.2f}, route={route_risk:.2f})."
        )

    @staticmethod
    def _build_decision(
        *,
        safety_payload: Dict[str, Any],
        route_payload: Dict[str, Any],
        emergency_payload: Dict[str, Any],
        anomaly_score: float,
    ) -> tuple[str, List[str]]:
        reasons: List[str] = []
        if emergency_payload["level"] == "CRITICAL":
            reasons.append("Critical emergency indicators detected")
            return "ALERT", reasons

        if safety_payload["risk_level"] in {"UNSAFE", "MODERATE"} and route_payload["route_risk"] >= settings.SAFETY_THRESHOLD:
            reasons.append("Elevated route exposure detected")
            return "REROUTE", reasons

        if safety_payload["risk_level"] == "UNSAFE":
            reasons.append("Overall safety ensemble flagged unsafe conditions")
            return "ESCALATE", reasons

        if anomaly_score >= 0.3:
            reasons.append("Behavioural anomaly monitoring recommended")
            return "MONITOR", reasons

        reasons.append("Risk profile remains within acceptable limits")
        return "STAY", reasons

    @staticmethod
    def _build_agent_summary(
        *,
        decision: str,
        reasons: List[str],
        safety_payload: Dict[str, Any],
        route_payload: Dict[str, Any],
        emergency_payload: Dict[str, Any],
        context: Dict[str, Any],
    ) -> str:
        return (
            f"Decision={decision}. Risk={safety_payload['risk_level']} ({safety_payload['risk_score']:.2f}). "
            f"Route={route_payload['recommended_route']} with route risk {route_payload['route_risk']:.2f}. "
            f"Emergency={emergency_payload['level']}. Context time={context.get('time_of_day', 'day')}. "
            f"Reason: {', '.join(reasons)}."
        )
