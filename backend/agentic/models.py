from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ToolDefinition:
    name: str
    description: str
    input_schema: Dict[str, Any]


@dataclass
class ToolExecutionResult:
    tool_name: str
    output: Dict[str, Any]
    rationale: str
    latency_ms: float


@dataclass
class AgentAction:
    tool_name: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    rationale: str = ""
    done: bool = False


@dataclass
class MemoryEvent:
    kind: str
    payload: Dict[str, Any]


@dataclass
class AgentRunSummary:
    session_id: str
    decision: str
    reasons: List[str]
    safety: Dict[str, Any]
    route: Dict[str, Any]
    emergency: Dict[str, Any]
    confidence: float
    tool_trace: List[Dict[str, Any]]
    agent_summary: str
    tools_used: List[str]
    planner_mode: str
    memory_size: int
