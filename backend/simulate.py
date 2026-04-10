import argparse
import asyncio
import json
import os
from typing import Any, Dict, List


def _load_steps_from_file(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "steps" in data:
        data = data["steps"]
    if not isinstance(data, list):
        raise ValueError("Expected a JSON array of step payloads (or an object with 'steps').")
    return data


async def _run(steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    from core.orchestrator import safety_app

    results: List[Dict[str, Any]] = []
    for step in steps:
        final_state = await safety_app.ainvoke({"payload": step, "status": "started"})
        results.append(
            {
                "status": final_state.get("status", "error"),
                "layer1_monitoring": final_state.get("safety_index", {}),
                "layer2_agents": final_state.get("orchestrator_decision", {}),
                "layer3_actions": final_state.get("action_results", {}),
                "timestamp": final_state.get("timestamp"),
            }
        )
    return results


def main():
    parser = argparse.ArgumentParser(description="Run Netrikan safety simulation locally.")
    parser.add_argument(
        "--scenario",
        default="normal",
        help="Built-in scenario id (normal, high_risk_no_sos, route_risk, sos, prompt_injection)",
    )
    parser.add_argument("--steps-json", default=None, help="Path to JSON file containing steps[]")
    args = parser.parse_args()

    # Force offline-safe defaults for simulation runs.
    os.environ.setdefault("NETRIKAN_AGENT_MODE", "sim")
    os.environ.setdefault("NETRIKAN_NO_NETWORK", "1")

    if args.steps_json:
        steps = _load_steps_from_file(args.steps_json)
        scenario_id = None
    else:
        from simulation.scenarios import get_scenario_steps

        scenario_id = args.scenario
        steps = get_scenario_steps(scenario_id)

    results = asyncio.run(_run(steps))
    print(json.dumps({"scenario_id": scenario_id, "results": results}, indent=2))


if __name__ == "__main__":
    main()
