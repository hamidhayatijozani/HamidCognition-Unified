from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import time
from datetime import datetime, timezone
from typing import Any

DB_PATH = os.getenv("ACTION_GATE_SECURITY_DB", "/data/action_gate_security.db")
WINDOW_SECONDS = int(os.getenv("ACTION_GATE_ANOMALY_WINDOW_SECONDS", "60"))
BURST_LIMIT = max(1, int(os.getenv("ACTION_GATE_ANOMALY_BURST_LIMIT", "20")))
ANOMALY_THRESHOLD = float(os.getenv("ACTION_GATE_ANOMALY_THRESHOLD", "0.80"))
TRIPWIRES = tuple(x.strip() for x in os.getenv("ACTION_GATE_TRIPWIRE_TARGETS", "").split(",") if x.strip())


def _connect() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    con = sqlite3.connect(DB_PATH, timeout=5)
    con.execute("PRAGMA busy_timeout=5000")
    con.execute(
        """CREATE TABLE IF NOT EXISTS security_events(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            event_type TEXT NOT NULL,
            tenant_id TEXT,
            agent_id TEXT,
            actor_id TEXT,
            session_id TEXT,
            action TEXT,
            target TEXT,
            decision TEXT,
            anomaly_score REAL,
            tripwire INTEGER NOT NULL DEFAULT 0,
            payload_json TEXT NOT NULL
        )"""
    )
    con.execute(
        """CREATE TABLE IF NOT EXISTS control_state(
            singleton INTEGER PRIMARY KEY CHECK(singleton=1),
            kill_switch INTEGER NOT NULL DEFAULT 0,
            reason TEXT,
            changed_at REAL NOT NULL
        )"""
    )
    con.execute(
        "INSERT OR IGNORE INTO control_state(singleton,kill_switch,reason,changed_at) VALUES(1,0,NULL,?)",
        (time.time(),),
    )
    con.commit()
    return con


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def set_kill_switch(active: bool, reason: str | None = None) -> dict[str, Any]:
    con = _connect()
    try:
        con.execute(
            "UPDATE control_state SET kill_switch=?, reason=?, changed_at=? WHERE singleton=1",
            (1 if active else 0, reason, time.time()),
        )
        con.commit()
        return security_status(con)
    finally:
        con.close()


def security_status(con: sqlite3.Connection | None = None) -> dict[str, Any]:
    own = con is None
    con = con or _connect()
    try:
        row = con.execute(
            "SELECT kill_switch, reason, changed_at FROM control_state WHERE singleton=1"
        ).fetchone()
        active = bool(row and row[0])
        return {
            "kill_switch": active,
            "reason": row[1] if row else None,
            "changed_at": datetime.fromtimestamp(row[2], timezone.utc).isoformat() if row else None,
            "tripwire_count": len(TRIPWIRES),
            "anomaly_window_seconds": WINDOW_SECONDS,
            "anomaly_burst_limit": BURST_LIMIT,
            "anomaly_threshold": ANOMALY_THRESHOLD,
        }
    finally:
        if own:
            con.close()


def is_kill_switch_active() -> bool:
    return bool(security_status()["kill_switch"])


def observe(
    *,
    event_type: str,
    tenant_id: str | None,
    agent_id: str | None,
    actor_id: str | None,
    session_id: str | None,
    action: str | None,
    target: str | None,
    decision: str | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    con = _connect()
    try:
        now = time.time()
        cutoff = now - WINDOW_SECONDS
        key = (tenant_id or "", agent_id or "", action or "")
        count = con.execute(
            """SELECT COUNT(*) FROM security_events
               WHERE ts >= ? AND tenant_id=? AND agent_id=? AND action=?""",
            (cutoff, *key),
        ).fetchone()[0]
        anomaly_score = min(1.0, (count + 1) / BURST_LIMIT)
        haystack = " ".join(x for x in (target or "", action or "") if x).lower()
        tripwire = any(pattern.lower() in haystack for pattern in TRIPWIRES)
        event = {
            "event_type": event_type,
            "tenant_id": tenant_id,
            "agent_id": agent_id,
            "actor_id": actor_id,
            "session_id": session_id,
            "action": action,
            "target": target,
            "decision": decision,
            "anomaly_score": anomaly_score,
            "tripwire": tripwire,
            "event_fingerprint": _fingerprint(payload or {}),
            "observed_at": datetime.fromtimestamp(now, timezone.utc).isoformat(),
        }
        con.execute(
            """INSERT INTO security_events(
               ts,event_type,tenant_id,agent_id,actor_id,session_id,action,target,
               decision,anomaly_score,tripwire,payload_json)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                now, event_type, tenant_id, agent_id, actor_id, session_id, action,
                target, decision, anomaly_score, 1 if tripwire else 0,
                json.dumps(event, sort_keys=True, separators=(",", ":"), default=str),
            ),
        )
        con.commit()
        event["kill_switch"] = security_status(con)["kill_switch"]
        event["anomaly_detected"] = anomaly_score >= ANOMALY_THRESHOLD
        return event
    finally:
        con.close()


def recent_events(limit: int = 100) -> list[dict[str, Any]]:
    con = _connect()
    try:
        rows = con.execute(
            "SELECT payload_json FROM security_events ORDER BY id DESC LIMIT ?",
            (max(1, min(limit, 1000)),),
        ).fetchall()
        return [json.loads(row[0]) for row in rows]
    finally:
        con.close()
