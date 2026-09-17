from datetime import datetime, timezone, timedelta

from product_gate import evaluate_product_gate, validate_meta_action


def valid(now):
    return {
        "action": "BUY_SMALL",
        "model_version": "model-001",
        "feature_version": "features-001",
        "input_hash": "abc123",
    }, {
        "timestamp": now.isoformat(),
        "connection_status": "CONNECTED",
        "input_hash": "abc123",
        "anomaly_score": 0.10,
        "drawdown": 0.02,
    }


def test_valid_proposal_passes():
    current = datetime.now(timezone.utc)
    proposal, observation = valid(current)
    result = evaluate_product_gate(proposal, observation, now=current)
    assert result.permitted is True
    assert result.decision == "ALLOW"


def test_missing_model_metadata_fails_closed():
    current = datetime.now(timezone.utc)
    proposal, observation = valid(current)
    proposal.pop("model_version")
    result = evaluate_product_gate(proposal, observation, now=current)
    assert result.permitted is False
    assert "missing_model_version" in result.reasons


def test_stale_observation_enters_safe_mode():
    current = datetime.now(timezone.utc)
    proposal, observation = valid(current - timedelta(seconds=6))
    result = evaluate_product_gate(proposal, observation, now=current)
    assert result.permitted is False
    assert result.decision == "SAFE_MODE"
    assert "stale_observation" in result.reasons


def test_input_hash_rebinding_is_rejected():
    current = datetime.now(timezone.utc)
    proposal, observation = valid(current)
    observation["input_hash"] = "different"
    result = evaluate_product_gate(proposal, observation, now=current)
    assert result.permitted is False
    assert "input_hash_mismatch" in result.reasons


def test_anomaly_and_drawdown_limits_fail_closed():
    current = datetime.now(timezone.utc)
    proposal, observation = valid(current)
    observation["anomaly_score"] = 0.81
    observation["drawdown"] = 0.11
    result = evaluate_product_gate(proposal, observation, now=current)
    assert result.permitted is False
    assert "anomaly_threshold_exceeded" in result.reasons
    assert "drawdown_limit_exceeded" in result.reasons


def test_unsupported_action_is_denied():
    current = datetime.now(timezone.utc)
    proposal, observation = valid(current)
    proposal["action"] = "TRANSFER_FUNDS"
    result = evaluate_product_gate(proposal, observation, now=current)
    assert result.permitted is False
    assert result.decision == "DENY"


def test_meta_controller_commands_are_bounded():
    assert validate_meta_action("ENTER_SAFE_MODE") is True
    assert validate_meta_action("EXECUTE_ANYTHING") is False
