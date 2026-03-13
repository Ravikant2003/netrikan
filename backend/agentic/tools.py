from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from agentic.models import ToolDefinition, ToolExecutionResult
from ml_models.predictor import predict_risk
from utils.crime_api import crime_score
from utils.maps_api import get_route


class BaseTool(ABC):
    name: str
    description: str
    input_schema: Dict[str, Any]

    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name=self.name,
            description=self.description,
            input_schema=self.input_schema,
        )

    def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> ToolExecutionResult:
        started_at = time.perf_counter()
        output = self._run(arguments=arguments, context=context)
        latency_ms = (time.perf_counter() - started_at) * 1000
        return ToolExecutionResult(
            tool_name=self.name,
            output=output,
            rationale=output.get("rationale", self.description),
            latency_ms=round(latency_ms, 2),
        )

    @abstractmethod
    def _run(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


class CrimeRiskTool(BaseTool):
    name = "crime_risk_lookup"
    description = "Estimate location risk from local crime intelligence and geographic context."
    input_schema = {
        "type": "object",
        "properties": {
            "latitude": {"type": "number"},
            "longitude": {"type": "number"},
        },
        "required": ["latitude", "longitude"],
    }

    def _run(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        latitude = float(arguments.get("latitude", context["latitude"]))
        longitude = float(arguments.get("longitude", context["longitude"]))
        score = crime_score(latitude, longitude)
        level = "HIGH" if score >= 0.65 else "MODERATE" if score >= 0.35 else "LOW"
        return {
            "crime_score": round(score, 4),
            "crime_level": level,
            "rationale": "Computed from local crime density features and geographic exposure.",
        }


class RouteAnalysisTool(BaseTool):
    name = "route_safety_analysis"
    description = "Estimate route distance, ETA, and route risk between origin and destination."
    input_schema = {
        "type": "object",
        "properties": {
            "start": {"type": "object"},
            "destination": {"type": "object"},
        },
        "required": ["start", "destination"],
    }

    def _run(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        start = arguments.get(
            "start",
            {"lat": context["latitude"], "lon": context["longitude"]},
        )
        destination = arguments.get("destination") or context.get("destination") or start
        route = get_route(start, destination)
        recommendation = "safer_alternate" if route["risk_weight"] >= 0.55 else "current_route"
        return {
            "recommended_route": recommendation,
            "distance_km": route["distance_km"],
            "eta_minutes": route["eta_minutes"],
            "route_risk": route["risk_weight"],
            "rationale": "Route scoring blends estimated travel exposure, congestion, and route risk.",
        }


class MLRiskPredictionTool(BaseTool):
    name = "ml_risk_prediction"
    description = "Predict situational safety risk using the trained XGBoost model."
    input_schema = {
        "type": "object",
        "properties": {
            "latitude": {"type": "number"},
            "longitude": {"type": "number"},
            "speed": {"type": "number"},
            "time_of_day": {"type": "string"},
            "severity": {"type": "string"},
        },
        "required": ["latitude", "longitude"],
    }

    def _run(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        latitude = float(arguments.get("latitude", context["latitude"]))
        longitude = float(arguments.get("longitude", context["longitude"]))
        speed = float(arguments.get("speed", context.get("speed", 0.0) or 0.0))
        time_of_day = str(arguments.get("time_of_day", context.get("time_of_day", "day")))
        severity = str(arguments.get("severity", context.get("severity", "low")))
        hour = self._parse_hour(time_of_day)
        risk = predict_risk(
            latitude=latitude,
            longitude=longitude,
            speed=int(speed),
            hour=hour,
            severity=severity,
        )
        return {
            "predicted_risk": round(float(risk), 4),
            "time_bucket": "night" if hour >= 22 or hour < 6 else "day",
            "severity": severity,
            "rationale": "Predicted by the trained XGBoost ensemble using mobility and temporal features.",
        }

    @staticmethod
    def _parse_hour(time_of_day: str) -> int:
        lowered = time_of_day.strip().lower()
        if lowered in {"night", "late_night"}:
            return 23
        if lowered in {"evening", "sunset"}:
            return 19
        if lowered in {"morning", "day", "afternoon"}:
            return 12
        if ":" in lowered:
            try:
                return max(0, min(23, int(lowered.split(":", maxsplit=1)[0])))
            except ValueError:
                return 12
        return 12


class EmergencyAssessmentTool(BaseTool):
    name = "emergency_signal_assessment"
    description = "Detect emergency severity from route deviation, speed, and distress signals."
    input_schema = {
        "type": "object",
        "properties": {
            "route_deviation": {"type": "boolean"},
            "text_signal": {"type": "string"},
            "speed": {"type": "number"},
        },
    }

    def _run(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        route_deviation = bool(arguments.get("route_deviation", context.get("route_deviation", False)))
        text_signal = str(arguments.get("text_signal", context.get("text_signal", ""))).lower()
        speed = float(arguments.get("speed", context.get("speed", 0.0) or 0.0))

        critical_terms = {"help", "save me", "emergency", "danger", "unsafe"}
        has_distress_signal = any(term in text_signal for term in critical_terms)
        anomaly_score = 0.0
        anomaly_score += 0.5 if route_deviation else 0.0
        anomaly_score += 0.7 if has_distress_signal else 0.0
        anomaly_score += 0.1 if speed > 90 else 0.0

        if anomaly_score >= 0.7:
            level = "CRITICAL"
            message = "Emergency indicators detected from distress signals and behavioural anomalies."
        elif anomaly_score >= 0.3:
            level = "ELEVATED"
            message = "Potential emergency indicators detected; heightened monitoring recommended."
        else:
            level = "NONE"
            message = "No immediate emergency indicators detected."

        return {
            "level": level,
            "message": message,
            "anomaly_score": round(anomaly_score, 4),
            "rationale": "Assessed from route deviation, distress language, and motion anomalies.",
        }


class ToolRegistry:
    def __init__(self, tools: List[BaseTool]):
        self._tools = {tool.name: tool for tool in tools}

    def definitions(self) -> List[ToolDefinition]:
        return [tool.definition() for tool in self._tools.values()]

    def has_tool(self, tool_name: str) -> bool:
        return tool_name in self._tools

    def execute(self, tool_name: str, arguments: Dict[str, Any], context: Dict[str, Any]) -> ToolExecutionResult:
        if tool_name not in self._tools:
            raise KeyError(f"Unknown tool requested: {tool_name}")
        return self._tools[tool_name].execute(arguments=arguments, context=context)

    @property
    def names(self) -> List[str]:
        return list(self._tools.keys())


def build_default_registry() -> ToolRegistry:
    return ToolRegistry(
        tools=[
            CrimeRiskTool(),
            RouteAnalysisTool(),
            MLRiskPredictionTool(),
            EmergencyAssessmentTool(),
        ]
    )
