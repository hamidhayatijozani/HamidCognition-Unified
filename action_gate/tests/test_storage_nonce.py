import json
from concurrent.futures import ThreadPoolExecutor

import storage


def _seed(tmp_path):
    storage.SQLITE_PATH = str(tmp_path / "nonce.db")
    storage.DATABASE_URL = None
    storage.init_db()
    record = {
        "decision_id": "dec-race",
        "trace_id": "trace-race",
        "nonce": "nonce-race",
        "consumed_at": None,
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


def test_nonce_can_only_be_consumed_once(tmp_path):
    _seed(tmp_path)

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(
            pool.map(
                lambda _: storage.consume_nonce("dec-race", "nonce-race", "2026-09-18T12:00:00+00:00"),
                range(8),
            )
        )

    assert results.count(True) == 1
    assert results.count(False) == 7

    con = storage.connect()
    try:
        row = con.execute(
            "SELECT json_extract(record, '$.consumed_at') FROM records WHERE decision_id=?",
            ("dec-race",),
        ).fetchone()
    finally:
        con.close()
    assert row[0] == "2026-09-18T12:00:00+00:00"


def test_wrong_nonce_cannot_consume_record(tmp_path):
    _seed(tmp_path)
    assert storage.consume_nonce("dec-race", "wrong", "2026-09-18T12:00:00+00:00") is False
