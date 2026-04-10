import pytest

from simulation.scenarios import get_scenario_steps, list_scenarios


def test_list_scenarios_is_stable():
    scenarios = list_scenarios()
    ids = {s["id"] for s in scenarios}
    assert {"normal", "route_risk", "sos", "prompt_injection"}.issubset(ids)


def test_get_scenario_steps_unknown_raises():
    with pytest.raises(ValueError):
        get_scenario_steps("does_not_exist")

