from __future__ import annotations

import json
import os
import sqlite3
import uuid
from typing import Any

import psycopg

from rate_limit import SlidingWindowRateLimiter

DATABASE_URL = os.getenv("ACTION_GATE_DATABASE_URL")
SQLITE_PATH = os.getenv("ACTION_GATE_DB", "action_gate.db")


def backend() -> str:
    return "postgresql" if DATABASE_URL and DATABASE_URL.startswith(("postgresql://", "postgres://")) else "sqlite"


def connect():
    if backend() == "postgresql":
        return psycopg.connect(DATABASE_URL)
    return sqlite3.connect(SQLITE_PATH)


def init_db() -> None:
    con = connect()
    try:
        if backend() == "postgresql":
            con.execute("CREATE TABLE IF NOT EXISTS records (decision_id TEXT PRIMARY KEY, trace_id TEXT, record TEXT NOT NULL)")
            con.execute("CREATE TABLE IF NOT EXISTS record_versions (version_id TEXT PRIMARY KEY, decision_id TEXT NOT NULL, version INTEGER NOT NULL, event_type TEXT NOT NULL, record TEXT NOT NULL, created_at TEXT NOT NULL, UNIQUE(decision_id, version))")
            con.execute("CREATE TABLE IF NOT EXISTS audit_events (event_id TEXT PRIMARY KEY, decision_id TEXT, event_type TEXT NOT NULL, event TEXT NOT NULL, previous_hash TEXT NOT NULL, event_hash TEXT NOT NULL, created_at TEXT NOT NULL)")
        else:
            con.execute("CREATE TABLE IF NOT EXISTS records (decision_id TEXT PRIMARY KEY, trace_id TEXT, record TEXT NOT NULL)")
            con.execute("CREATE TABLE IF NOT EXISTS record_versions (version_id TEXT PRIMARY KEY, decision_id TEXT NOT NULL, version INTEGER NOT NULL, event_type TEXT NOT NULL, record TEXT NOT NULL, created_at TEXT NOT NULL, UNIQUE(decision_id, version))")
            con.execute("CREATE TABLE IF NOT EXISTS audit_events (event_id TEXT PRIMARY KEY, decision_id TEXT, event_type TEXT NOT NULL, event TEXT NOT NULL, previous_hash TEXT NOT NULL, event_hash TEXT NOT NULL, created_at TEXT NOT NULL)")
            con.execute("CREATE TRIGGER IF NOT EXISTS audit_events_no_update BEFORE UPDATE ON audit_events BEGIN SELECT RAISE(ABORT, 'audit_events_are_append_only'); END")
            con.execute("CREATE TRIGGER IF NOT EXISTS audit_events_no_delete BEFORE DELETE ON audit_events BEGIN SELECT RAISE(ABORT, 'audit_events_are_append_only'); END")
        con.commit()
    finally:
        con.close()


def health() -> dict[str, Any]:
    con = connect()
    try:
        con.execute("SELECT 1").fetchone()
        return {"status": "ok", "backend": backend()}
    except Exception as exc:
        return {"status": "degraded", "backend": backend(), "error": type(exc).__name__}
    finally:
        con.close()


def save_record(record: dict[str, Any], event_type: str, digest_fn, canonical_fn, now_fn) -> None:
    con = connect()
    try:
        if backend() == "postgresql":
            con.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (record["decision_id"],))
            current = con.execute("SELECT COALESCE(MAX(version), 0) FROM record_versions WHERE decision_id=%s", (record["decision_id"],)).fetchone()[0]
            previous = con.execute("SELECT event_hash FROM audit_events ORDER BY created_at DESC, event_id DESC LIMIT 1").fetchone()
        else:
            current = con.execute("SELECT COALESCE(MAX(version), 0) FROM record_versions WHERE decision_id=?", (record["decision_id"],)).fetchone()[0]
            previous = con.execute("SELECT event_hash FROM audit_events ORDER BY rowid DESC LIMIT 1").fetchone()
        version = current + 1
        previous_hash = previous[0] if previous else "GENESIS"
        event = {"decision": record["decision"], "tenant_id": record["tenant_id"], "action_hash": record["action_hash"], "version": version}
        event_hash = digest_fn({"decision_id": record["decision_id"], "event_type": event_type, "event": event, "previous_hash": previous_hash})
        record["audit_event_hash"] = event_hash
        event_id = f"evt_{uuid.uuid4().hex}"
        version_id = f"ver_{uuid.uuid4().hex}"
        timestamp = now_fn()
        if backend() == "postgresql":
            con.execute("INSERT INTO audit_events VALUES (%s,%s,%s,%s,%s,%s,%s)", (event_id, record["decision_id"], event_type, canonical_fn(event), previous_hash, event_hash, timestamp))
            con.execute("INSERT INTO record_versions VALUES (%s,%s,%s,%s,%s,%s)", (version_id, record["decision_id"], version, event_type, canonical_fn(record), timestamp))
            con.execute("INSERT INTO records VALUES (%s,%s,%s) ON CONFLICT (decision_id) DO UPDATE SET trace_id=EXCLUDED.trace_id, record=EXCLUDED.record", (record["decision_id"], record["trace_id"], canonical_fn(record)))
        else:
            con.execute("INSERT INTO audit_events VALUES (?,?,?,?,?,?,?)", (event_id, record["decision_id"], event_type, canonical_fn(event), previous_hash, event_hash, timestamp))
            con.execute("INSERT INTO record_versions VALUES (?,?,?,?,?,?)", (version_id, record["decision_id"], version, event_type, canonical_fn(record), timestamp))
            con.execute("INSERT OR REPLACE INTO records VALUES (?,?,?)", (record["decision_id"], record["trace_id"], canonical_fn(record)))
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def load_record(decision_id: str) -> str | None:
    con = connect()
    try:
        if backend() == "postgresql":
            row = con.execute("SELECT record FROM records WHERE decision_id=%s", (decision_id,)).fetchone()
        else:
            row = con.execute("SELECT record FROM records WHERE decision_id=?", (decision_id,)).fetchone()
        return row[0] if row else None
    finally:
        con.close()
