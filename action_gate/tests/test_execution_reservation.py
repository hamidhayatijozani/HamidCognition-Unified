import json
from concurrent.futures import ThreadPoolExecutor

import storage


def _seed(tmp_path):
    storage.SQLITE_PATH = str(tmp_path / "reserve.db")
    storage.DATABASE_URL = None
    storage.init_db()
    record = {
        "decision_id": "dec-reserve",
        "trace_id": "trace-reserve",
        "nonce": "nonce-reserve",
        "consumed_at": None,
        "execution_started_at": None,
    }
    con = storage.connect()
    try:
        con.execute(
            "INSERT INTO records(decision_id, trace_id, record) VALUES (?, ?, ?)",
            (record["decision_id"], record["trace_id"], json.dumps(record)),
        )
        con.commit()
    finally:
        con.close()


def test_concurrent_reservation_has_single_winner(tmp_path):
    _seed(tmp_path)
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(
            pool.map(
                lambda _: storage.reserve_execution(
                    "dec-reserve", "nonce-reserve", "2026-09-18T13:00:00+00:00"
                ),
                range(8),
            )
        )
    assert results.count(True) == 1
    assert results.count(False) == 7
