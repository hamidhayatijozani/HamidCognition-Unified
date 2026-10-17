"""Runtime proof for persistent, atomic execution-authority nonce consumption.

These tests exercise the configured SQLite backend used by the Action Gate MVP.
They do not claim PostgreSQL production parity; that requires a separate live
PostgreSQL integration run.
"""
from concurrent.futures import ThreadPoolExecutor

import storage


def _use_isolated_db(tmp_path):
    storage.SQLITE_PATH = str(tmp_path / "authority-nonces.db")
    storage.DATABASE_URL = None
    storage.init_db()


def test_authority_nonce_survives_database_reconnect(tmp_path):
    _use_isolated_db(tmp_path)

    assert storage.consume_authority_nonce(
        "nonce-persist-001", "decision-001", "2026-10-16T00:00:00+00:00"
    ) is True

    # Re-open the same database through the storage layer, simulating process
    # restart/reinitialization rather than relying on an in-memory set.
    storage.init_db()
    assert storage.consume_authority_nonce(
        "nonce-persist-001", "decision-001", "2026-10-16T00:00:01+00:00"
    ) is False


def test_concurrent_authority_nonce_consumption_has_one_winner(tmp_path):
    _use_isolated_db(tmp_path)

    def consume(_):
        return storage.consume_authority_nonce(
            "nonce-race-001", "decision-race-001", "2026-10-16T00:01:00+00:00"
        )

    with ThreadPoolExecutor(max_workers=12) as pool:
        results = list(pool.map(consume, range(12)))

    assert results.count(True) == 1
    assert results.count(False) == 11


def test_authority_nonce_cannot_be_reused_by_another_decision(tmp_path):
    _use_isolated_db(tmp_path)

    assert storage.consume_authority_nonce(
        "nonce-cross-decision-001", "decision-a", "2026-10-16T00:02:00+00:00"
    ) is True
    assert storage.consume_authority_nonce(
        "nonce-cross-decision-001", "decision-b", "2026-10-16T00:02:01+00:00"
    ) is False
