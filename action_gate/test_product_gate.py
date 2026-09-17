from datetime import datetime, timezone, timedelta

from observation_boundary import validate_observation
from product_gate import evaluate_product_gate, validate_meta_action


def valid(now):
    stamp = now.isoformat()
    observation = {
        "timestamp": stamp,
        "symbol": "EURUSD",
        "bid": 1.1000,
        "ask": 1.1002,
        "tick_id": "tick-001",
        "sequence": 10,
        "broker_timestamp": stamp,
        "local_timestamp": stamp,
        "connection_status": "CONNECTED",
        "anomaly_score": 0.10,
        "drawdown": 0.02,
    }
    boundary = validate_observation(observation, now=now)
    proposal = {
        "action": "BUY_SMALL",
        "model_version": "model-001",
        "feature_version": "features-001",
        "input_hash": boundary.observation_hash,
    }
    return proposal, observation, boundary


def test_valid_proposal_passes():
    current = datetime.now(timezone.utc)
    proposal, observation, boundary = valid(current)
    result = evaluate_product_gate(proposal, observation, boundary, now=current)
    assert result.permitted is True
    assert result.decision == "ALLOW"


def test_missing_model_metadata_fails_closed():
    current = datetime.now(timezone.utc)
    proposal, observation, boundary = valid(current)
    proposal.pop("model_version")
    result = evaluate_product_gate(proposal, observation, boundary, now=current)
    assert result.permitted is False
    assert "missing_model_version" in result.reasons


def test_stale_observation_enters_safe_mode_at_boundary():
    current = datetime.now(timezone.utc)
    proposal, observation, boundary = valid(current - timedelta(seconds=6))
    result = evaluate_product_gate(proposal, observation, boundary, now=current)
    assert boundary.permitted is False
    assert result.permitted is False
    assert result.decision == "SAFE_MODE"
    assert "observation_boundary_rejected" in result.reasons


def test_boundary_rebinding_is_rejected():
    current = datetime.now(timezone.utc)
    proposal, observation, boundary = valid(current)
    proposal["input_hash"] = "different"
    result = evaluate_product_gate(proposal, observation, boundary, now=current)
    assert result.permitted is False
    assert "input_hash_mismatch" in result.reasons


def test_anomaly_and_drawdown_limits_fail_closed():
    current = datetime.now(timezone.utc)
    proposal, observation, boundary = valid(current)
    observation["anomaly_score"] = 0.81
    observation["drawdown"] = 0.11
    result = evaluate_product_gate(proposal, observation, boundary, now=current)
    assert result.permitted is False
    assert "anomaly_threshold_exceeded" in result.reasons
    assert "drawdown_limit_exceeded" in result.reasons


def test_unsupported_action_is_denied():
    current = datetime.now(timezone.utc)
    proposal, observation, boundary = valid(current)
    proposal["action"] = "TRANSFER_FUNDS"
    result = evaluate_product_gate(proposal, observation, boundary, now=current)
    assert result.permitted is False
    assert result.decision == "DENY"


def test_missing_boundary_is_not_authority():
    current = datetime.now(timezone.utc)
    proposal, observation, _ = valid(current)
    result = evaluate_product_gate(
        proposal,
        observation,
        validate_observation({"timestamp": current.isoformat()}, now=current),
        now=current,
    )
    assert result.permitted is False
    assert result.decision == "DENY"


def test_meta_controller_commands_are_bounded():
    assert validate_meta_action("ENTER_SAFE_MODE") is True
    assert validate_meta_action("EXECUTE_ANYTHING") is False
