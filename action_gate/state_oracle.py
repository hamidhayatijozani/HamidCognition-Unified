from __future__ import annotations

import hashlib
import hmac
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from storage import backend, connect

STATE_ORACLE_SECRET = os.getenv("ACTION_GATE_STATE_ORACLE_SECRET")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def snapshot_hash(snapshot: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical(snapshot).encode("utf-8")).hexdigest()


def ensure_state_table() -> None:
    con = connect()
    try:
        con.execute(
            "CREATE TABLE IF NOT EXISTS state_snapshots ("
            "snapshot_id TEXT PRIMARY KEY, world_version TEXT UNIQUE NOT NULL, "
            "snapshot_hash TEXT NOT NULL, snapshot TEXT NOT NULL, committed_at TEXT NOT NULL)"
        )
        con.commit()
    finally:
        con.close()


def get_current_snapshot() -> dict[str, Any] | None:
    ensure_state_table()
    con = connect()
    try:
        row = con.execute(
            "SELECT snapshot_id, world_version, snapshot_hash, snapshot, committed_at "
            "FROM state_snapshots ORDER BY committed_at DESC, snapshot_id DESC LIMIT 1"
        ).fetchone()
        if not row:
            return None
        return {
            "snapshot_id": row[0],
            "world_version": row[1],
            "snapshot_hash": row[2],
            "snapshot": json.loads(row[3]),
            "committed_at": row[4],
        }
    finally:
        con.close()


def commit_snapshot(snapshot: dict[str, Any], world_version: str | None = None) -> dict[str, Any]:
    ensure_state_table()
    version = world_version or f"wv_{uuid.uuid4().hex}"
    committed_at = datetime.now(timezone.utc).isoformat()
    result = {
        "snapshot_id": f"snap_{uuid.uuid4().hex}",
        "world_version": version,
        "snapshot_hash": snapshot_hash(snapshot),
        "snapshot": snapshot,
        "committed_at": committed_at,
    }
    con = connect()
    try:
        if backend() == "postgresql":
            con.execute(
                "INSERT INTO state_snapshots(snapshot_id,world_version,snapshot_hash,snapshot,committed_at) "
                "VALUES (%s,%s,%s,%s,%s)",
                (result["snapshot_id"], version, result["snapshot_hash"], _canonical(snapshot), committed_at),
            )
        else:
            con.execute(
                "INSERT INTO state_snapshots(snapshot_id,world_version,snapshot_hash,snapshot,committed_at) "
                "VALUES (?,?,?,?,?)",
                (result["snapshot_id"], version, result["snapshot_hash"], _canonical(snapshot), committed_at),
            )
        con.commit()
        return result
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def verify_commit_signature(payload: dict[str, Any], signature: str | None) -> bool:
    if not STATE_ORACLE_SECRET or not signature:
        return False
    expected = hmac.new(
        STATE_ORACLE_SECRET.encode("utf-8"),
        _canonical(payload).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
