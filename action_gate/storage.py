from __future__ import annotations

import json
import os
import sqlite3
import uuid
from typing import Any

import psycopg

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
        con.execute("CREATE TABLE IF NOT EXISTS records (decision_id TEXT PRIMARY KEY, trace_id TEXT, record TEXT NOT NULL)")
        con.execute("CREATE TABLE IF NOT EXISTS record_versions (version_id TEXT PRIMARY KEY, decision_id TEXT NOT NULL, version INTEGER NOT NULL, event_type TEXT NOT NULL, record TEXT NOT NULL, created_at TEXT NOT NULL, UNIQUE(decision_id, version))")
        con.execute("CREATE TABLE IF NOT EXISTS audit_events (event_id TEXT PRIMARY KEY, decision_id TEXT, event_type TEXT NOT NULL, event TEXT NOT NULL, previous_hash TEXT NOT NULL, event_hash TEXT NOT NULL, created_at TEXT NOT NULL)")
        con.execute("CREATE TABLE IF NOT EXISTS idempotency_keys (tenant_id TEXT NOT NULL, idempotency_key TEXT NOT NULL, request_digest TEXT NOT NULL, response TEXT NOT NULL, created_at TEXT NOT NULL, PRIMARY KEY (tenant_id, idempotency_key))")
        con.execute("CREATE TABLE IF NOT EXISTS validation_events (event_id TEXT PRIMARY KEY, correlation_id TEXT NOT NULL, tenant_id TEXT, request_id TEXT, idempotency_key TEXT, request_digest TEXT, validation_result TEXT NOT NULL, error_code TEXT, raw_request TEXT NOT NULL, created_at TEXT NOT NULL)")
        con.execute("CREATE TABLE IF NOT EXISTS rate_limit_events (event_id TEXT PRIMARY KEY, rate_key TEXT NOT NULL, created_at REAL NOT NULL)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_rate_limit_events_key_time ON rate_limit_events(rate_key, created_at)")
        con.commit()
        if backend() == "sqlite":
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


def load_idempotency(tenant_id: str, idempotency_key: str) -> tuple[str, str] | None:
    con = connect()
    try:
        if backend() == "postgresql":
            row = con.execute("SELECT request_digest, response FROM idempotency_keys WHERE tenant_id=%s AND idempotency_key=%s", (tenant_id, idempotency_key)).fetchone()
        else:
            row = con.execute("SELECT request_digest, response FROM idempotency_keys WHERE tenant_id=? AND idempotency_key=?", (tenant_id, idempotency_key)).fetchone()
        return (row[0], row[1]) if row else None
    finally:
        con.close()


def save_idempotency(tenant_id: str, idempotency_key: str, request_digest: str, response: str, created_at: str) -> bool:
    con = connect()
    try:
        if backend() == "postgresql":
            row = con.execute("INSERT INTO idempotency_keys VALUES (%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING RETURNING tenant_id", (tenant_id, idempotency_key, request_digest, response, created_at)).fetchone()
        else:
            con.execute("INSERT OR IGNORE INTO idempotency_keys VALUES (?,?,?,?,?)", (tenant_id, idempotency_key, request_digest, response, created_at))
            row = con.execute("SELECT changes()").fetchone()
        con.commit()
        return bool(row)
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def save_validation_event(*, correlation_id: str, tenant_id: str | None, request_id: str | None, idempotency_key: str | None, request_digest: str | None, validation_result: str, error_code: str | None, raw_request: str, created_at: str) -> None:
    con = connect()
    event_id = f"val_{uuid.uuid4().hex}"
    try:
        if backend() == "postgresql":
            con.execute("INSERT INTO validation_events VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (event_id, correlation_id, tenant_id, request_id, idempotency_key, request_digest, validation_result, error_code, raw_request, created_at))
        else:
            con.execute("INSERT INTO validation_events VALUES (?,?,?,?,?,?,?,?,?,?)", (event_id, correlation_id, tenant_id, request_id, idempotency_key, request_digest, validation_result, error_code, raw_request, created_at))
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def load_validation_request(tenant_id: str, request_id: str) -> str | None:
    con = connect()
    try:
        if backend() == "postgresql":
            row = con.execute("SELECT raw_request FROM validation_events WHERE tenant_id=%s AND request_id=%s AND validation_result='PASS' ORDER BY created_at DESC LIMIT 1", (tenant_id, request_id)).fetchone()
        else:
            row = con.execute("SELECT raw_request FROM validation_events WHERE tenant_id=? AND request_id=? AND validation_result='PASS' ORDER BY created_at DESC LIMIT 1", (tenant_id, request_id)).fetchone()
        return row[0] if row else None
    finally:
        con.close()


def save_record(record: dict[str, Any], event_type: str, digest_fn, canonical_fn, now_fn) -> None:
    con = connect()
    try:
        if backend() == "postgresql":
            con.execute("SELECT pg_advisory_xact_lock(%s)", (2147483000,))
            con.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (record["decision_id"],))
            current = con.execute("SELECT COALESCE(MAX(version), 0) FROM record_versions WHERE decision_id=%s", (record["decision_id"],)).fetchone()[0]
            previous = con.execute("SELECT event_hash FROM audit_events ORDER BY created_at DESC, event_id DESC LIMIT 1").fetchone()
        else:
            con.execute("BEGIN IMMEDIATE")
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


def reserve_execution(decision_id: str, nonce: str, started_at: str) -> bool:
    """Atomically reserve a one-time execution before any external side effect."""
    con = connect()
    try:
        if backend() == "postgresql":
            con.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (decision_id,))
            row = con.execute(
                "UPDATE records SET record = jsonb_set(record::jsonb, '{execution_started_at}', to_jsonb(%s::text), false)::text "
                "WHERE decision_id=%s AND (record::jsonb->>'nonce')=%s "
                "AND (record::jsonb->>'consumed_at') IS NULL AND (record::jsonb->>'execution_started_at') IS NULL "
                "RETURNING decision_id",
                (started_at, decision_id, nonce),
            ).fetchone()
        else:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute(
                "UPDATE records SET record = json_set(record, '$.execution_started_at', ?) "
                "WHERE decision_id=? AND json_extract(record, '$.nonce')=? "
                "AND json_extract(record, '$.consumed_at') IS NULL AND json_extract(record, '$.execution_started_at') IS NULL",
                (started_at, decision_id, nonce),
            )
            row = (decision_id,) if row.rowcount == 1 else None
        con.commit()
        return bool(row)
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def finalize_execution(record: dict[str, Any], nonce: str, consumed_at: str, digest_fn, canonical_fn, now_fn, outcome: dict[str, Any]) -> dict[str, Any] | None:
    """Atomically finalize an execution and persist its outcome/evidence in one DB transaction."""
    con = connect()
    try:
        decision_id = record["decision_id"]
        if backend() == "postgresql":
            con.execute("SELECT pg_advisory_xact_lock(%s)", (2147483000,))
            con.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (decision_id,))
            row = con.execute(
                "SELECT record FROM records WHERE decision_id=%s", (decision_id,)
            ).fetchone()
        else:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute(
                "SELECT record FROM records WHERE decision_id=?", (decision_id,)
            ).fetchone()
        if not row:
            con.rollback()
            return False
        current = json.loads(row[0])
        if current.get("nonce") != nonce or current.get("consumed_at") is not None or current.get("execution_started_at") is None:
            con.rollback()
            return False
        finalized = dict(record)
        finalized["execution"] = {"timestamp": consumed_at, "status": "EXECUTED", "action_hash": current["action_hash"], "nonce": nonce}
        finalized["outcome"] = outcome
        finalized["consumed_at"] = consumed_at
        current_version = con.execute(
            "SELECT COALESCE(MAX(version), 0) FROM record_versions WHERE decision_id=" + ("%s" if backend() == "postgresql" else "?"),
            (decision_id,),
        ).fetchone()[0]
        previous = con.execute(
            "SELECT event_hash FROM audit_events ORDER BY created_at DESC, event_id DESC LIMIT 1"
        ).fetchone()
        version = current_version + 1
        previous_hash = previous[0] if previous else "GENESIS"
        event = {"decision": finalized["decision"], "tenant_id": finalized["tenant_id"], "action_hash": finalized["action_hash"], "version": version}
        event_hash = digest_fn({"decision_id": decision_id, "event_type": "EXECUTION_RECORDED", "event": event, "previous_hash": previous_hash})
        finalized["audit_event_hash"] = event_hash
        finalized["evidence_hash"] = digest_fn(finalized)
        event_id = f"evt_{uuid.uuid4().hex}"
        version_id = f"ver_{uuid.uuid4().hex}"
        timestamp = now_fn()
        event_json = canonical_fn(event)
        record_json = canonical_fn(finalized)
        if backend() == "postgresql":
            con.execute("INSERT INTO audit_events VALUES (%s,%s,%s,%s,%s,%s,%s)", (event_id, decision_id, "EXECUTION_RECORDED", event_json, previous_hash, event_hash, timestamp))
            con.execute("INSERT INTO record_versions VALUES (%s,%s,%s,%s,%s,%s)", (version_id, decision_id, version, "EXECUTION_RECORDED", record_json, timestamp))
            updated = con.execute(
                "UPDATE records SET trace_id=%s, record=%s WHERE decision_id=%s AND (record::jsonb->>'nonce')=%s AND (record::jsonb->>'consumed_at') IS NULL AND (record::jsonb->>'execution_started_at') IS NOT NULL RETURNING decision_id",
                (finalized["trace_id"], record_json, decision_id, nonce),
            ).fetchone()
        else:
            con.execute("INSERT INTO audit_events VALUES (?,?,?,?,?,?,?)", (event_id, decision_id, "EXECUTION_RECORDED", event_json, previous_hash, event_hash, timestamp))
            con.execute("INSERT INTO record_versions VALUES (?,?,?,?,?,?)", (version_id, decision_id, version, "EXECUTION_RECORDED", record_json, timestamp))
            updated = con.execute(
                "UPDATE records SET trace_id=?, record=? WHERE decision_id=? AND json_extract(record, '$.nonce')=? AND json_extract(record, '$.consumed_at') IS NULL AND json_extract(record, '$.execution_started_at') IS NOT NULL",
                (finalized["trace_id"], record_json, decision_id, nonce),
            )
            updated = (decision_id,) if updated.rowcount == 1 else None
        if not updated:
            con.rollback()
            return False
        con.commit()
        return finalized
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def consume_nonce(decision_id: str, nonce: str, consumed_at: str) -> bool:
    """Atomically claim a decision nonce exactly once across processes/replicas."""
    con = connect()
    try:
        if backend() == "postgresql":
            row = con.execute(
                "UPDATE records SET record = jsonb_set(record::jsonb, '{consumed_at}', to_jsonb(%s::text), false)::text "
                "WHERE decision_id=%s AND (record::jsonb->>'nonce')=%s AND (record::jsonb->>'consumed_at') IS NULL "
                "RETURNING decision_id",
                (consumed_at, decision_id, nonce),
            ).fetchone()
        else:
            row = con.execute(
                "UPDATE records SET record = json_set(record, '$.consumed_at', ?) "
                "WHERE decision_id=? AND json_extract(record, '$.nonce')=? "
                "AND json_extract(record, '$.consumed_at') IS NULL",
                (consumed_at, decision_id, nonce),
            )
            row = (decision_id,) if row.rowcount == 1 else None
        con.commit()
        return bool(row)
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def allow_rate_limit(rate_key: str, limit: int, window_seconds: int, now_ts: float) -> bool:
    """Atomically enforce a shared rate limit using the configured database."""
    if limit <= 0 or window_seconds <= 0:
        return False
    con = connect()
    try:
        cutoff = now_ts - window_seconds
        if backend() == "postgresql":
            con.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (rate_key,))
            con.execute("DELETE FROM rate_limit_events WHERE rate_key=%s AND created_at<=%s", (rate_key, cutoff))
            count = con.execute("SELECT COUNT(*) FROM rate_limit_events WHERE rate_key=%s", (rate_key,)).fetchone()[0]
            if count >= limit:
                con.rollback()
                return False
            con.execute("INSERT INTO rate_limit_events VALUES (%s,%s,%s)", (f"rl_{uuid.uuid4().hex}", rate_key, now_ts))
        else:
            con.execute("BEGIN IMMEDIATE")
            con.execute("DELETE FROM rate_limit_events WHERE rate_key=? AND created_at<=?", (rate_key, cutoff))
            count = con.execute("SELECT COUNT(*) FROM rate_limit_events WHERE rate_key=?", (rate_key,)).fetchone()[0]
            if count >= limit:
                con.rollback()
                return False
            con.execute("INSERT INTO rate_limit_events VALUES (?,?,?)", (f"rl_{uuid.uuid4().hex}", rate_key, now_ts))
        con.commit()
        return True
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


init_db()
