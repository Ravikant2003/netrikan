from __future__ import annotations

import statistics
import time
from collections import Counter
from pathlib import Path
from typing import Callable, Dict, List

import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from agentic.orchestrator import AgenticSafetyOrchestrator


PayloadFactory = Callable[[int], Dict[str, object]]


def build_baseline(iteration: int) -> Dict[str, object]:
    return {
        "latitude": 12.9716,
        "longitude": 77.5946,
        "destination": {"lat": 12.9352, "lon": 77.6245},
        "time_of_day": "day",
        "speed": 24.0 + (iteration % 4),
        "severity": "medium",
        "route_deviation": False,
        "text_signal": "",
        "session_id": f"benchmark-baseline-{iteration % 5}",
    }


def build_night_high_risk(iteration: int) -> Dict[str, object]:
    return {
        "latitude": 12.961 + iteration * 0.0001,
        "longitude": 77.601 + iteration * 0.0001,
        "destination": {"lat": 12.925, "lon": 77.644},
        "time_of_day": "23:00",
        "speed": 82.0,
        "severity": "high",
        "route_deviation": False,
        "text_signal": "",
        "session_id": f"benchmark-night-{iteration % 5}",
    }


def build_emergency(iteration: int) -> Dict[str, object]:
    return {
        "latitude": 12.949 + iteration * 0.0001,
        "longitude": 77.618 + iteration * 0.0001,
        "destination": {"lat": 12.932, "lon": 77.652},
        "time_of_day": "night",
        "speed": 12.0,
        "severity": "high",
        "route_deviation": True,
        "text_signal": "help me now",
        "session_id": f"benchmark-emergency-{iteration % 5}",
    }


def build_no_destination(iteration: int) -> Dict[str, object]:
    return {
        "latitude": 12.9716,
        "longitude": 77.5946,
        "time_of_day": "afternoon",
        "speed": 18.0,
        "severity": "low",
        "route_deviation": False,
        "text_signal": "",
        "session_id": f"benchmark-fallback-{iteration % 5}",
    }


def percentile(values: List[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round((len(ordered) - 1) * fraction))))
    return ordered[index]


def benchmark_scenario(
    orchestrator: AgenticSafetyOrchestrator,
    name: str,
    payload_factory: PayloadFactory,
    iterations: int,
) -> Dict[str, object]:
    latencies_ms: List[float] = []
    decisions: Counter[str] = Counter()
    planner_modes: Counter[str] = Counter()

    for iteration in range(iterations):
        payload = payload_factory(iteration)
        started_at = time.perf_counter()
        result = orchestrator.run(payload)
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        latencies_ms.append(elapsed_ms)
        decisions[result["decision"]] += 1
        planner_modes[result["planner_mode"]] += 1

    return {
        "scenario": name,
        "iterations": iterations,
        "avg_latency_ms": round(statistics.mean(latencies_ms), 2),
        "median_latency_ms": round(statistics.median(latencies_ms), 2),
        "p95_latency_ms": round(percentile(latencies_ms, 0.95), 2),
        "max_latency_ms": round(max(latencies_ms), 2),
        "decision_distribution": dict(decisions),
        "planner_modes": dict(planner_modes),
    }


def main() -> None:
    orchestrator = AgenticSafetyOrchestrator()
    scenarios = [
        ("baseline", build_baseline),
        ("night_high_risk", build_night_high_risk),
        ("critical_emergency", build_emergency),
        ("no_destination_fallback", build_no_destination),
    ]
    iterations = 25

    results = [
        benchmark_scenario(orchestrator, name, factory, iterations)
        for name, factory in scenarios
    ]

    print("Agentic Runtime Benchmark Results")
    print("=" * 72)
    for result in results:
        print(f"Scenario: {result['scenario']}")
        print(f"  Iterations: {result['iterations']}")
        print(f"  Avg Latency: {result['avg_latency_ms']} ms")
        print(f"  Median Latency: {result['median_latency_ms']} ms")
        print(f"  P95 Latency: {result['p95_latency_ms']} ms")
        print(f"  Max Latency: {result['max_latency_ms']} ms")
        print(f"  Decisions: {result['decision_distribution']}")
        print(f"  Planner Modes: {result['planner_modes']}")
        print("-" * 72)


if __name__ == "__main__":
    main()
