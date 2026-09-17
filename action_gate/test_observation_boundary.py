from datetime import datetime, timezone, timedelta

from observation_boundary import observation_hash, validate_observation


def valid(now):
    stamp = now.isoformat()
    return {
        "timestamp": stamp,
        "symbol": "EURUSD",
        "bid": 1.1000,
        "ask": 1.1002,
        "tick_id": "tick-001",
        "sequence": 10,
        "broker_timestamp": stamp,
        "local_timestamp": stamp,
        "connection_status": "CONNECTED",
        "volume": 100,
    }


def test_valid_observation_is_admitted_and_hashed():
    now = datetime.now(timezone.utc)
    observation = valid(now)
    result = validate_observation(observation, now=now)
    assert result.permitted is True
    assert result.decision == "ALLOW"
    assert result.observation_hash == observation_hash(observation)


def test_missing_required_metadata_fails_closed():
    now = datetime.now(timezone.utc)
    observation = valid(now)
    del observation["tick_id"]
    result = validate_observation(observation, now=now)
    assert result.permitted is False
    assert "missing_required_fields:tick_id" in result.reasons


def test_stale_observation_enters_safe_mode():
    now = datetime.now(timezone.utc)
    observation = valid(now - timedelta(seconds=6))
    result = validate_observation(observation, now=now)
    assert result.decision == "SAFE_MODE"
    assert "stale_observation" in result.reasons


def test_future_observation_enters_safe_mode():
    now = datetime.now(timezone.utc)
    observation = valid(now + timedelta(seconds=1))
    result = validate_observation(observation, now=now)
    assert result.decision == "SAFE_MODE"
    assert "future_observation" in result.reasons


def test_duplicate_tick_is_rejected():
    now = datetime.now(timezone.utc)
    observation = valid(now)
    result = validate_observation(observation, now=now, seen_tick_ids={"tick-001"})
    assert result.decision == "SAFE_MODE"
    assert "duplicate_tick_id" in result.reasons


def test_sequence_gap_is_rejected():
    now = datetime.now(timezone.utc)
    observation = valid(now)
    observation["sequence"] = 12
    result = validate_observation(observation, now=now, previous_sequence=10)
    assert result.decision == "SAFE_MODE"
    assert "sequence_gap" in result.reasons


def test_disconnected_feed_cannot_pass():
    now = datetime.now(timezone.utc)
    observation = valid(now)
    observation["connection_status"] = "DISCONNECTED"
    result = validate_observation(observation, now=now)
    assert result.decision == "SAFE_MODE"
    assert "connection_not_connected" in result.reasons


def test_negative_spread_is_denied():
    now = datetime.now(timezone.utc)
    observation = valid(now)
    observation["bid"] = 1.101
    observation["ask"] = 1.100
    result = validate_observation(observation, now=now)
    assert result.decision == "DENY"
    assert "negative_spread" in result.reasons


def test_hash_changes_when_observation_changes():
    now = datetime.now(timezone.utc)
    observation = valid(now)
    first = observation_hash(observation)
    observation["ask"] = 1.1003
    second = observation_hash(observation)
    assert first != second


def test_sequence_is_optional_but_if_present_must_be_contiguous():
    now = datetime.now(timezone.utc)
    observation = valid(now)
    observation.pop("sequence")
    result = validate_observation(observation, now=now, previous_sequence=10)
    assert result.permitted is True
