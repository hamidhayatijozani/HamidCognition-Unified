from __future__ import annotations

import hmac
import os
from typing import Any

import psycopg
from fastapi import FastAPI, Header, HTTPException
from psycopg.types.json import Jsonb

from .engine import Evidence, EvidenceRelation, SignalSnapshot

app = FastAPI(title="ClaimLab Evidence API", version="1.0.0")


def require_api_key(x_claimlab_api_key: str | None) -> None:
    expected = os.getenv("CLAIMLAB_API_KEY", "").strip()
    if not expected:
        raise RuntimeError("CLAIMLAB_API_KEY is required for evidence writes")
    if not x_claimlab_api_key or not hmac.compare_digest(x_claimlab_api_key, expected):
        raise HTTPException(status_code=401, detail="invalid_api_key")


def database_url() -> str:
    value = os.getenv("DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("DATABASE_URL is required")
    return value


def ensure_schema() -> None:
    with psycopg.connect(database_url()) as db:
        with db.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS evidence (
                    evidence_id TEXT PRIMARY KEY,
                    relation TEXT NOT NULL,
                    source TEXT NOT NULL,
                    statement TEXT NOT NULL,
                    strength DOUBLE PRECISION NOT NULL DEFAULT 1.0,
                    fresh BOOLEAN NOT NULL DEFAULT TRUE,
                    independent BOOLEAN NOT NULL DEFAULT TRUE,
                    signals JSONB,
                    evidence_type TEXT NOT NULL DEFAULT 'generic',
                    timestamp TEXT NOT NULL DEFAULT ''
                )
            """)
            cur.execute("ALTER TABLE evidence ADD COLUMN IF NOT EXISTS signals JSONB")
            cur.execute("ALTER TABLE evidence ADD COLUMN IF NOT EXISTS evidence_type TEXT NOT NULL DEFAULT 'generic'")
            cur.execute("ALTER TABLE evidence ADD COLUMN IF NOT EXISTS timestamp TEXT NOT NULL DEFAULT ''")
            cur.execute("CREATE INDEX IF NOT EXISTS evidence_type_idx ON evidence (evidence_type)")
        db.commit()


def row_to_payload(row: tuple[Any, ...]) -> dict[str, Any]:
    (
        evidence_id, relation, source, statement, strength, fresh,
        independent, signals, evidence_type, timestamp,
    ) = row
    return {
        "evidence_id": evidence_id,
        "relation": relation,
        "source": source,
        "statement": statement,
        "strength": strength,
        "fresh": fresh,
        "independent": independent,
        "signals": signals,
        "evidence_type": evidence_type,
        "timestamp": timestamp,
    }


@app.on_event("startup")
def startup() -> None:
    ensure_schema()


@app.get("/health")
def health() -> dict[str, str]:
    try:
        with psycopg.connect(database_url()) as db:
            db.execute("SELECT 1")
        return {"status": "ok", "database": "ok"}
    except Exception:
        raise HTTPException(status_code=503, detail="database_unavailable")


@app.post("/evidence", status_code=201)
def create_evidence(request: dict[str, Any], x_claimlab_api_key: str | None = Header(default=None)) -> dict[str, Any]:
    require_api_key(x_claimlab_api_key)
    try:
        snapshot = SignalSnapshot(**request["signals"])
        evidence = Evidence(
            evidence_id=str(request["id"]),
            relation=EvidenceRelation(request.get("relation", "SUPPORT")),
            source=str(request.get("source", "signal-feed")),
            statement=str(request.get("statement", "signal snapshot")),
            strength=float(request.get("strength", 1.0)),
            fresh=bool(request.get("fresh", True)),
            independent=bool(request.get("independent", True)),
            signals=snapshot,
            evidence_type=str(request.get("type", "signal_snapshot")),
            timestamp=str(request.get("timestamp", "")),
        )
        payload = evidence.to_dict()
        with psycopg.connect(database_url()) as db:
            with db.cursor() as cur:
                cur.execute("""
                    INSERT INTO evidence
                    (evidence_id, relation, source, statement, strength, fresh,
                     independent, signals, evidence_type, timestamp)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (evidence_id) DO UPDATE SET
                      relation=EXCLUDED.relation,
                      source=EXCLUDED.source,
                      statement=EXCLUDED.statement,
                      strength=EXCLUDED.strength,
                      fresh=EXCLUDED.fresh,
                      independent=EXCLUDED.independent,
                      signals=EXCLUDED.signals,
                      evidence_type=EXCLUDED.evidence_type,
                      timestamp=EXCLUDED.timestamp
                """, (
                    evidence.evidence_id, evidence.relation.value, evidence.source,
                    evidence.statement, evidence.strength, evidence.fresh,
                    evidence.independent, Jsonb(payload["signals"]),
                    evidence.evidence_type, evidence.timestamp,
                ))
            db.commit()
        return payload
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/evidence/{evidence_id}")
def get_evidence(evidence_id: str) -> dict[str, Any]:
    with psycopg.connect(database_url()) as db:
        with db.cursor() as cur:
            cur.execute("""
                SELECT evidence_id, relation, source, statement, strength, fresh,
                       independent, signals, evidence_type, timestamp
                FROM evidence WHERE evidence_id=%s
            """, (evidence_id,))
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="not_found")
    return row_to_payload(row)
