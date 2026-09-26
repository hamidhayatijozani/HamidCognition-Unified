import json
from pathlib import Path

from canonical_engine import CanonicalPST, CONFIG


def test_weights_are_explicit_and_normalized_contract_is_present():
    assert CONFIG["version"] == "PST-CANONICAL-1.0"
    assert CONFIG["transition_weights"] == {"P": 0.05, "S": 0.04, "T": 0.03}
    assert CONFIG["initial_state"] == {"P": 0.88, "S": 0.78, "T": 0.40}


def test_first_transition_is_reproducible():
    engine = CanonicalPST()
    result = engine.step(0.85, 0.75)
    assert result["P"] == 0.9055
    assert result["S"] == 0.7917
    assert result["T"] == 0.4251


def test_weight_change_cannot_be_implicit():
    text = Path(__file__).with_name("canonical_engine.py").read_text(encoding="utf-8")
    assert "w_p = CONFIG[\"transition_weights\"][\"P\"]" in text
    assert "w_s = CONFIG[\"transition_weights\"][\"S\"]" in text
    assert "w_t = CONFIG[\"transition_weights\"][\"T\"]" in text
