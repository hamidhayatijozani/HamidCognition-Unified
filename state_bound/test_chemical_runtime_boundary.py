from __future__ import annotations

import json
import subprocess
import sys


def test_importing_state_bound_does_not_load_action_gate_modules():
    code = (
        "import state_bound, sys; "
        "assert not any(name == 'action_gate' or name.startswith('action_gate.') "
        "for name in sys.modules)"
    )
    result = subprocess.run([sys.executable, "-c", code], check=False)
    assert result.returncode == 0


def test_reactivity_is_deterministic_across_processes():
    code = """
import json
from state_bound.chemical_reactivity import ReactivityFactors, calculate_reactivity
f = ReactivityFactors(0.8, 0.1, 0.9, 0.95, 0.9, 0.92)
r = calculate_reactivity(f)
print(json.dumps({
    "mode": r.mode,
    "reactivity": r.reactivity,
    "activation_margin": r.activation_margin,
    "reason": r.reason,
}, sort_keys=True))
"""
    outputs = [
        subprocess.check_output([sys.executable, "-c", code], text=True).strip()
        for _ in range(2)
    ]
    assert outputs[0] == outputs[1]
    json.loads(outputs[0])


def test_research_layer_never_returns_execution_authority():
    from state_bound.chemical_reactivity import ReactivityFactors, calculate_reactivity

    result = calculate_reactivity(ReactivityFactors(1.0, 0.0, 1.0, 1.0, 1.0, 1.0))
    assert not hasattr(result, "authority")
    assert result.mode == "PROCEED"
