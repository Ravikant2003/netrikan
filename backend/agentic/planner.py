from __future__ import annotations

import json
from typing import Any, Dict, List

import httpx

from agentic.models import AgentAction, ToolDefinition
from config import settings


class HeuristicPlanner:
    mode = "heuristic"

    def next_action(
        self,
        *,
        context: Dict[str, Any],
        tool_trace: List[Dict[str, Any]],
        available_tools: List[ToolDefinition],
    ) -> AgentAction:
        completed_tools = {step["tool_name"] for step in tool_trace}
        destination = context.get("destination") or {}

        if "crime_risk_lookup" not in completed_tools:
            return AgentAction(
                tool_name="crime_risk_lookup",
                arguments={
                    "latitude": context["latitude"],
                    "longitude": context["longitude"],
                },
                rationale="Estimate static environmental risk before making route decisions.",
            )

        if "ml_risk_prediction" not in completed_tools:
            return AgentAction(
                tool_name="ml_risk_prediction",
                arguments={
                    "latitude": context["latitude"],
                    "longitude": context["longitude"],
                    "speed": context.get("speed", 0.0),
                    "time_of_day": context.get("time_of_day", "day"),
                    "severity": context.get("severity", "low"),
                },
                rationale="Use the trained ML model for high-signal dynamic risk estimation.",
            )

        if destination and "route_safety_analysis" not in completed_tools:
            return AgentAction(
                tool_name="route_safety_analysis",
                arguments={
                    "start": {"lat": context["latitude"], "lon": context["longitude"]},
                    "destination": destination,
                },
                rationale="Evaluate route exposure before finalizing the mobility recommendation.",
            )

        if "emergency_signal_assessment" not in completed_tools:
            return AgentAction(
                tool_name="emergency_signal_assessment",
                arguments={
                    "route_deviation": context.get("route_deviation", False),
                    "text_signal": context.get("text_signal", ""),
                    "speed": context.get("speed", 0.0),
                },
                rationale="Check for urgent behavioural signals before returning the final decision.",
            )

        return AgentAction(tool_name="", done=True, rationale="All required specialist tools have executed.")


class LLMPlanner:
    mode = "llm"

    def __init__(self) -> None:
        self._fallback = HeuristicPlanner()

    def next_action(
        self,
        *,
        context: Dict[str, Any],
        tool_trace: List[Dict[str, Any]],
        available_tools: List[ToolDefinition],
    ) -> AgentAction:
        if not self._can_use_llm():
            return self._fallback.next_action(
                context=context,
                tool_trace=tool_trace,
                available_tools=available_tools,
            )

        payload = self._build_payload(
            context=context,
            tool_trace=tool_trace,
            available_tools=available_tools,
        )

        try:
            response = httpx.post(
                f"{settings.LLM_API_BASE.rstrip('/')}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.LLM_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=settings.LLM_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            message = response.json()["choices"][0]["message"]["content"]
            decision = self._parse_llm_response(message)
            if decision.tool_name and any(tool.name == decision.tool_name for tool in available_tools):
                return decision
        except Exception:
            pass

        return self._fallback.next_action(
            context=context,
            tool_trace=tool_trace,
            available_tools=available_tools,
        )

    @staticmethod
    def _can_use_llm() -> bool:
        return bool(
            settings.AGENT_USE_LLM
            and settings.LLM_API_BASE
            and settings.LLM_API_KEY
            and settings.LLM_MODEL
        )

    @staticmethod
    def _parse_llm_response(message: str) -> AgentAction:
        parsed = json.loads(message)
        return AgentAction(
            tool_name=parsed.get("tool_name", ""),
            arguments=parsed.get("arguments", {}),
            rationale=parsed.get("rationale", ""),
            done=bool(parsed.get("done", False)),
        )

    @staticmethod
    def _build_payload(
        *,
        context: Dict[str, Any],
        tool_trace: List[Dict[str, Any]],
        available_tools: List[ToolDefinition],
    ) -> Dict[str, Any]:
        tool_specs = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
            }
            for tool in available_tools
        ]

        system_prompt = (
            "You are a safety-critical routing orchestrator. "
            "Select exactly one next tool for the current situation. "
            "Return valid JSON only with keys: tool_name, arguments, rationale, done."
        )

        user_prompt = {
            "context": context,
            "tool_trace": tool_trace,
            "tools": tool_specs,
            "instructions": [
                "Prefer ML risk and route tools before finalizing.",
                "Use emergency assessment if any distress or route deviation is present.",
                "Set done=true only when enough evidence has been collected.",
            ],
        }

        return {
            "model": settings.LLM_MODEL,
            "temperature": 0.1,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_prompt)},
            ],
            "response_format": {"type": "json_object"},
        }


def build_planner():
    if settings.AGENT_USE_LLM:
        return LLMPlanner()
    return HeuristicPlanner()
