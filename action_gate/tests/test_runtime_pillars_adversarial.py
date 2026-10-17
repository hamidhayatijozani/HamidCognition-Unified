"""Adversarial pillar tests for the Action Gate execution boundary.

What these tests exercise, and nothing more:

  P1 authority binding      security_authority.issue_authority / verify_authority
  P2 atomic single use      storage.consume_authority_nonce / reserve_execution
                            (SQLite backend; threads and separate OS processes)
  P3 append-only ledger     storage.save_record -> audit_events (SQLite) and the
                            in-memory evidence_ledger.EvidenceLedger
  P4 deterministic replay   recorded verifier inputs replayed in fresh processes
                            under different hash seeds
  P5 four-state fail-closed only the exact string ALLOW is executable

Evidence boundary:
  * Unit / integration level. No HTTP or MCP endpoint is exercised.
  * SQLite only. PostgreSQL behaviour is not tested here.
  * Replay covers the gate verdict (verify_authority) for recorded inputs. It
    does not replay how a decision was produced upstream.
  * No external ledger anchor was found in action_gate/ when this file was
    written. Tests that mention an anchor show why one is needed; they do not
    implement one.

Naming convention:
  * test_gap_*             strict expected failures. Each asserts the behaviour a
                           gate should have and currently fails. When a gap is
                           fixed the test starts passing, the runner reports an
                           unexpected success (a failure), and the decorator
                           must be removed.
  * test_characterization_*  pins down current behaviour that is worth knowing
                           about. Not an endorsement of that behaviour.

Run:  cd action_gate && PYTHONPATH=. pytest -q tests/test_runtime_pillars_adversarial.py
"""
from __future__ import annotations

import base64
import dataclasses
import datetime
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import textwrap
import threading
import time
import unittest
from contextlib import closing

import storage
from evidence_ledger import EvidenceLedger
from security_authority import (
    Authority,
    AuthorityError,
    canonical_json,
    issue_authority,
    verify_authority,
)

ACTION_GATE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET = b"pillars-adversarial-secret"
TENANT = "tenant-a"
NOW = 10_000
ACTION = {"action": "transfer_funds", "amount": 5, "to": "acct-1"}
POLICY = {"version": "pillars-policy", "rules": ["a", "b"]}
STAMP = "2026-01-01T00:00:00+00:00"


# --------------------------------------------------------------------------- helpers


def issue(**overrides) -> Authority:
    kwargs = dict(
        secret=SECRET, decision_id="dec-1", tenant_id=TENANT, action=ACTION,
        policy=POLICY, decision="ALLOW", ttl_seconds=60, now=NOW,
        nonce="nonce-1", key_id="key-1",
    )
    kwargs.update(overrides)
    return issue_authority(**kwargs)


def verdict(authority: Authority, **overrides) -> str:
    """'ACCEPT', or the AuthorityError text. Any other exception propagates."""
    kwargs = dict(
        authority=authority, secret=SECRET, tenant_id=TENANT,
        action=ACTION, policy=POLICY, now=NOW + 1,
    )
    kwargs.update(overrides)
    try:
        verify_authority(**kwargs)
    except AuthorityError as exc:
        return str(exc)
    return "ACCEPT"


def race(parties: int, fn):
    """Run fn(i) in `parties` threads that are released together by a barrier."""
    barrier = threading.Barrier(parties, timeout=30)
    results: list = [None] * parties
    errors: list[str] = []

    def runner(i: int) -> None:
        try:
            barrier.wait()
            results[i] = fn(i)
        except BaseException as exc:  # surfaced below, never swallowed
            errors.append(repr(exc))

    threads = [threading.Thread(target=runner, args=(i,), daemon=True) for i in range(parties)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(60)
    if errors or any(thread.is_alive() for thread in threads):
        raise AssertionError(f"race harness failure: {errors or 'a thread did not finish'}")
    return results


def _digest(obj) -> str:
    return hashlib.sha256(canonical_json(obj).encode()).hexdigest()


def _record(i: int) -> dict:
    return {
        "decision_id": f"dec-{i}", "trace_id": f"trace-{i}", "decision": "ALLOW",
        "tenant_id": TENANT, "action_hash": f"action-hash-{i}",
    }


def _save(record: dict) -> None:
    storage.save_record(record, "DECISION", _digest, canonical_json, lambda: STAMP)


def _audit_rows(path: str) -> list[tuple]:
    with closing(sqlite3.connect(path, timeout=10)) as con:
        return con.execute(
            "SELECT rowid, event_id, decision_id, event_type, event, previous_hash, event_hash "
            "FROM audit_events ORDER BY rowid"
        ).fetchall()


def _chain_problems(rows: list[tuple]) -> list[str]:
    """Recompute an audit chain from its stored rows (same recipe as storage.save_record)."""
    problems, previous = [], "GENESIS"
    for rowid, _event_id, decision_id, event_type, event, previous_hash, event_hash in rows:
        if previous_hash != previous:
            problems.append(f"row {rowid}: previous_hash does not link to the prior event")
        expected = _digest({
            "decision_id": decision_id, "event_type": event_type,
            "event": json.loads(event), "previous_hash": previous_hash,
        })
        if expected != event_hash:
            problems.append(f"row {rowid}: event_hash does not match its content")
        previous = event_hash
    return problems


class StorageCase(unittest.TestCase):
    """Each test gets its own SQLite file; storage module globals are always restored."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory(prefix="ag-pillars-")
        self.addCleanup(tmp.cleanup)
        self.addCleanup(self._restore, storage.SQLITE_PATH, storage.DATABASE_URL)
        self.db_path = os.path.join(tmp.name, "pillars.db")
        storage.SQLITE_PATH = self.db_path
        storage.DATABASE_URL = None
        storage.init_db()

    @staticmethod
    def _restore(path, url) -> None:
        storage.SQLITE_PATH = path
        storage.DATABASE_URL = url

    def child_env(self) -> dict:
        env = dict(os.environ)
        env["ACTION_GATE_DB"] = self.db_path
        env.pop("ACTION_GATE_DATABASE_URL", None)
        env["PYTHONPATH"] = os.pathsep.join(filter(None, [ACTION_GATE_DIR, env.get("PYTHONPATH")]))
        return env


# --------------------------------------------------------------------------- P1


class AuthorityBinding(unittest.TestCase):
    def test_every_signed_field_is_tamper_evident(self):
        """Flip each signed field while keeping the old signature. Every flip must
        be caught by the signature itself, so the verification context is chosen
        so that no other check could reject it first."""
        allow = issue()
        ask = issue(decision="ASK")
        replace = dataclasses.replace
        cases = {
            "decision_id": (replace(allow, decision_id="dec-2"), {}),
            "tenant_id": (replace(allow, tenant_id="tenant-b"), {"tenant_id": "tenant-b"}),
            "action_digest": (replace(allow, action_digest="0" * 64), {"action": None}),
            "policy_digest": (replace(allow, policy_digest="f" * 64), {"policy": None}),
            "nonce": (replace(allow, nonce="nonce-forged"), {}),
            "issued_at": (replace(allow, issued_at=NOW - 100), {}),
            "expires_at": (replace(allow, expires_at=NOW + 10_000), {}),
            "decision": (replace(ask, decision="ALLOW"), {}),
            "key_id": (replace(allow, key_id="key-2"), {}),
        }
        signed_fields = {f.name for f in dataclasses.fields(Authority)} - {"signature"}
        self.assertEqual(
            set(cases), signed_fields,
            "Authority changed: add a tamper case for every new signed field",
        )
        leaks = {
            field: got
            for field, (authority, ctx) in cases.items()
            if (got := verdict(authority, **ctx)) != "invalid_signature"
        }
        self.assertEqual(leaks, {}, "fields not covered by the signature")

    def test_token_tamper_cannot_escalate_a_non_executable_decision(self):
        original = issue(decision="DENY")
        token = original.token()
        self.assertEqual(Authority.from_token(token), original)
        data = json.loads(base64.urlsafe_b64decode(token + "=" * (-len(token) % 4)))
        data["decision"] = "ALLOW"
        forged = base64.urlsafe_b64encode(json.dumps(data).encode()).decode().rstrip("=")
        self.assertEqual(verdict(Authority.from_token(forged)), "invalid_signature")
        self.assertEqual(verdict(Authority.from_token(token)), "decision_not_executable")

    def test_malformed_tokens_fail_closed(self):
        good = dataclasses.asdict(issue())

        def b64(obj) -> str:
            raw = obj if isinstance(obj, bytes) else json.dumps(obj).encode()
            return base64.urlsafe_b64encode(raw).decode().rstrip("=")

        tokens = {
            "empty": "",
            "not base64": "%%%not-base64%%%",
            "not json": b64(b"not json"),
            "json list": b64([]),
            "extra field": b64({**good, "admin": True}),
            "missing nonce": b64({k: v for k, v in good.items() if k != "nonce"}),
        }
        escaped = {}
        for name, token in tokens.items():
            try:
                Authority.from_token(token)
                escaped[name] = "parsed"
            except AuthorityError:
                pass
            except Exception as exc:  # any other type breaks the fail-closed contract
                escaped[name] = type(exc).__name__
        self.assertEqual(escaped, {})

    def test_wrong_secret_is_rejected(self):
        self.assertEqual(verdict(issue(), secret=b"another-secret"), "invalid_signature")

    def test_validity_window_edges(self):
        authority = issue()  # valid for NOW <= t < NOW + 60
        expected = {
            NOW - 1: "expired_or_not_yet_valid",
            NOW: "ACCEPT",
            NOW + 59: "ACCEPT",
            NOW + 60: "expired_or_not_yet_valid",
        }
        self.assertEqual({t: verdict(authority, now=t) for t in expected}, expected)

    def test_rejected_verifications_do_not_consume_the_nonce(self):
        authority = issue()
        registry: set[str] = set()
        bad_contexts = [
            {"tenant_id": "tenant-b"},
            {"now": NOW + 60},
            {"now": NOW - 1},
            {"action": {"action": "other"}},
            {"policy": {"version": "other"}},
            {"secret": b"wrong-secret"},
        ]
        outcomes = [verdict(authority, used_nonces=registry, **ctx) for ctx in bad_contexts]
        self.assertNotIn("ACCEPT", outcomes)
        self.assertEqual(registry, set())
        self.assertEqual(verdict(authority, used_nonces=registry), "ACCEPT")
        self.assertEqual(registry, {"nonce-1"})
        self.assertEqual(verdict(authority, used_nonces=registry), "nonce_reuse")

    def test_characterization_omitted_binding_is_skipped(self):
        """verify_authority treats action=None / policy=None as 'do not check'.
        Callers must always pass both; an omitted binding accepts any action."""
        authority = issue()
        other_action = {"action": "delete_database"}
        self.assertEqual(verdict(authority, action=other_action), "action_binding_mismatch")
        self.assertEqual(verdict(authority, action=None, policy=None), "ACCEPT")


# --------------------------------------------------------------------------- P2

_CLAIM_CHILD = textwrap.dedent(
    """
    import sys, time
    import storage

    start_at, nonce, who = float(sys.argv[1]), sys.argv[2], sys.argv[3]
    while True:
        remaining = start_at - time.time()
        if remaining <= 0:
            break
        time.sleep(min(remaining, 0.002))
    won = storage.consume_authority_nonce(nonce, "decision-" + who, "2026-01-01T00:00:00+00:00")
    print("WIN" if won else "LOSE")
    """
)


class AtomicConsumption(StorageCase):
    @staticmethod
    def _reap(proc) -> None:
        if proc.poll() is None:
            proc.kill()
        proc.wait()

    def test_barrier_race_has_exactly_one_winner(self):
        results = race(16, lambda i: storage.consume_authority_nonce("nonce-race", f"dec-{i}", STAMP))
        self.assertEqual(results.count(True), 1, results)

    def test_the_race_harness_detects_a_check_then_act_claim(self):
        """Control. A deliberately broken claim (read, wait for everyone, then
        write) must yield several winners under the same harness. If it did not,
        the single-winner assertions in this class would prove nothing."""
        parties = 8
        gate = threading.Barrier(parties, timeout=30)

        def naive_claim(i: int) -> bool:
            con = storage.connect()
            try:
                seen = con.execute(
                    "SELECT 1 FROM authority_nonces WHERE nonce=?", ("nonce-naive",)
                ).fetchone() is not None
                gate.wait()  # every claimant has now observed 'unused'
                con.execute(
                    "INSERT OR IGNORE INTO authority_nonces (nonce, decision_id, consumed_at) VALUES (?,?,?)",
                    ("nonce-naive", f"dec-{i}", STAMP),
                )
                con.commit()
                return not seen
            finally:
                con.close()

        winners = race(parties, naive_claim).count(True)
        self.assertGreater(winners, 1, "harness failed to expose a non-atomic claim")

    def test_separate_processes_have_one_winner_and_a_restart_cannot_replay(self):
        env = self.child_env()
        start_at = time.time() + 3.0
        procs = [
            subprocess.Popen(
                [sys.executable, "-c", _CLAIM_CHILD, str(start_at), "nonce-proc", str(i)],
                env=env, cwd=ACTION_GATE_DIR,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            )
            for i in range(6)
        ]
        for proc in procs:
            self.addCleanup(self._reap, proc)
        outputs = [proc.communicate(timeout=120) for proc in procs]
        self.assertEqual([proc.returncode for proc in procs], [0] * 6, outputs)
        votes = sorted(out.strip() for out, _err in outputs)
        self.assertEqual(votes, ["LOSE"] * 5 + ["WIN"], outputs)
        # A brand-new process after every other one exited: the claim must persist.
        late = subprocess.run(
            [sys.executable, "-c", _CLAIM_CHILD, "0", "nonce-proc", "late"],
            env=env, cwd=ACTION_GATE_DIR, capture_output=True, text=True, timeout=120,
        )
        self.assertEqual(late.stdout.strip(), "LOSE", late.stderr)

    def test_execution_reservation_has_exactly_one_winner(self):
        record = {"decision_id": "dec-r", "nonce": "nonce-r", "decision": "ALLOW"}
        with closing(storage.connect()) as con:
            con.execute("INSERT INTO records VALUES (?,?,?)", ("dec-r", "trace-r", json.dumps(record)))
            con.commit()
        self.assertFalse(storage.reserve_execution("dec-r", "wrong-nonce", STAMP))
        results = race(16, lambda i: storage.reserve_execution("dec-r", "nonce-r", STAMP))
        self.assertEqual(results.count(True), 1, results)
        self.assertFalse(storage.reserve_execution("dec-r", "nonce-r", STAMP))

    def test_characterization_purging_below_authority_lifetime_reopens_replay(self):
        """purge_authority_nonces knows nothing about authority lifetimes. A
        retention shorter than the authority TTL (plus clock skew) lets a still
        valid authority be consumed a second time."""
        t0 = datetime.datetime.fromisoformat(STAMP).timestamp()
        self.assertTrue(storage.consume_authority_nonce("nonce-purge", "dec-p", STAMP))
        self.assertEqual(storage.purge_authority_nonces(300, now_ts=t0 + 30), 0)
        self.assertFalse(storage.consume_authority_nonce("nonce-purge", "dec-p", STAMP))
        self.assertEqual(storage.purge_authority_nonces(0, now_ts=t0 + 30), 1)
        self.assertTrue(
            storage.consume_authority_nonce("nonce-purge", "dec-p", STAMP),
            "nonce was purged, so the same authority is accepted again",
        )


# --------------------------------------------------------------------------- P3


class AppendOnlyLedger(StorageCase):
    def test_persisted_chain_stays_linear_under_concurrent_writers(self):
        race(16, lambda i: _save(_record(i)))
        rows = _audit_rows(self.db_path)
        self.assertEqual(len(rows), 16)
        self.assertEqual(_chain_problems(rows), [])
        self.assertEqual(len({row[5] for row in rows}), 16, "two events share a previous_hash (fork)")

    def test_concurrent_saves_of_one_decision_get_unique_versions(self):
        race(8, lambda i: _save(_record(0)))
        with closing(sqlite3.connect(self.db_path, timeout=10)) as con:
            versions = sorted(
                v for (v,) in con.execute("SELECT version FROM record_versions WHERE decision_id=?", ("dec-0",))
            )
        self.assertEqual(versions, list(range(1, 9)))
        self.assertEqual(_chain_problems(_audit_rows(self.db_path)), [])

    def test_update_and_delete_on_audit_events_are_rejected(self):
        _save(_record(1))
        before = _audit_rows(self.db_path)
        for sql in ("UPDATE audit_events SET event_hash = 'forged'", "DELETE FROM audit_events"):
            with closing(sqlite3.connect(self.db_path, timeout=10)) as con:
                with self.assertRaisesRegex(sqlite3.DatabaseError, "append_only"):
                    con.execute(sql)
        self.assertEqual(_audit_rows(self.db_path), before)

    def test_naive_tamper_is_detected_but_a_privileged_rewrite_needs_an_external_anchor(self):
        for i in range(5):
            _save(_record(i))
        rows = _audit_rows(self.db_path)
        exported_head = rows[-1][6]  # what an external anchor would have stored
        self.assertEqual(_chain_problems(rows), [])

        forged_event = '{"action_hash":"x","decision":"DENY","tenant_id":"tenant-a","version":1}'
        with closing(sqlite3.connect(self.db_path, timeout=10)) as con:
            con.execute("DROP TRIGGER audit_events_no_update")  # needs DDL rights
            # 1) naive tamper: change content, leave every hash alone
            con.execute("UPDATE audit_events SET event = ? WHERE rowid = ?", (forged_event, rows[2][0]))
            con.commit()
            self.assertNotEqual(_chain_problems(_audit_rows(self.db_path)), [], "naive tamper went unnoticed")
            # 2) full rewrite: recompute the forged event and every later link
            current = _audit_rows(self.db_path)
            previous = current[1][6]
            for rowid, _eid, decision_id, event_type, event, _old_prev, _old_hash in current[2:]:
                new_hash = _digest({
                    "decision_id": decision_id, "event_type": event_type,
                    "event": json.loads(event), "previous_hash": previous,
                })
                con.execute(
                    "UPDATE audit_events SET previous_hash = ?, event_hash = ? WHERE rowid = ?",
                    (previous, new_hash, rowid),
                )
                previous = new_hash
            con.commit()
        rewritten = _audit_rows(self.db_path)
        self.assertEqual(_chain_problems(rewritten), [], "a full rewrite looks internally valid")
        self.assertNotEqual(rewritten[-1][6], exported_head, "an exported head hash exposes the rewrite")


class InMemoryLedger(unittest.TestCase):
    @staticmethod
    def _ledger(n: int = 5) -> EvidenceLedger:
        ledger = EvidenceLedger()
        for i in range(n):
            ledger.append(f"e{i}", "DECISION", "trace", {"i": i})
        return ledger

    def test_reorder_and_middle_deletion_are_detected(self):
        swapped = self._ledger()
        swapped._events[1], swapped._events[2] = swapped._events[2], swapped._events[1]
        self.assertFalse(swapped.verify_chain())
        holed = self._ledger()
        del holed._events[2]
        self.assertFalse(holed.verify_chain())

    def test_characterization_tail_truncation_is_invisible_without_a_recorded_head(self):
        ledger = self._ledger()
        recorded_head = ledger.events()[-1].event_hash
        del ledger._events[3:]
        self.assertTrue(ledger.verify_chain())
        self.assertNotEqual(ledger.events()[-1].event_hash, recorded_head)


# --------------------------------------------------------------------------- P4

_REPLAY_CHILD = textwrap.dedent(
    """
    import json, sys
    from security_authority import Authority, AuthorityError, verify_authority

    secret = sys.argv[1].encode()
    out = []
    for case in json.load(sys.stdin):
        try:
            verify_authority(authority=Authority.from_token(case["token"]), secret=secret,
                             tenant_id=case["tenant_id"], action=case["action"],
                             policy=case["policy"], now=case["now"])
            out.append("ACCEPT")
        except AuthorityError as exc:
            out.append(str(exc))
    print(json.dumps(out))
    """
)


def _replay_corpus() -> list[dict]:
    base = issue()
    unicode_action = {"action": "note", "text": "caf" + chr(0xE9) + " " + "".join(map(chr, (0x633, 0x644, 0x627, 0x645)))}
    reordered_action = {"to": "acct-1", "amount": 5, "action": "transfer_funds"}
    reordered_policy = {"rules": ["a", "b"], "version": "pillars-policy"}
    cases = [
        ("valid", base, TENANT, ACTION, POLICY, NOW + 1),
        ("same content, other key order", base, TENANT, reordered_action, reordered_policy, NOW + 1),
        ("tenant", base, "tenant-b", ACTION, POLICY, NOW + 1),
        ("expired", base, TENANT, ACTION, POLICY, NOW + 60),
        ("not yet valid", base, TENANT, ACTION, POLICY, NOW - 1),
        ("action", base, TENANT, {"action": "other"}, POLICY, NOW + 1),
        ("policy", base, TENANT, ACTION, {"version": "other"}, NOW + 1),
        ("ask", issue(decision="ASK"), TENANT, ACTION, POLICY, NOW + 1),
        ("sandbox", issue(decision="SANDBOX"), TENANT, ACTION, POLICY, NOW + 1),
        ("deny", issue(decision="DENY"), TENANT, ACTION, POLICY, NOW + 1),
        ("bad signature", dataclasses.replace(base, signature="0" * 64), TENANT, ACTION, POLICY, NOW + 1),
        ("unicode", issue(action=unicode_action), TENANT, unicode_action, POLICY, NOW + 1),
    ]
    return [
        {"name": name, "token": authority.token(), "tenant_id": tenant,
         "action": action, "policy": policy, "now": now}
        for name, authority, tenant, action, policy, now in cases
    ]


class DeterministicReplay(unittest.TestCase):
    def test_issuance_is_deterministic_for_recorded_inputs(self):
        first, second = issue(), issue()
        self.assertEqual(first, second)
        self.assertEqual(first.token(), second.token())

    def test_recorded_verdicts_replay_identically_across_processes_and_hash_seeds(self):
        corpus = _replay_corpus()
        expected = [
            verdict(Authority.from_token(c["token"]), tenant_id=c["tenant_id"],
                    action=c["action"], policy=c["policy"], now=c["now"])
            for c in corpus
        ]
        self.assertEqual(
            set(expected),
            {"ACCEPT", "tenant_mismatch", "expired_or_not_yet_valid", "action_binding_mismatch",
             "policy_binding_mismatch", "decision_not_executable", "invalid_signature"},
            "the corpus must exercise every verdict class",
        )
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join(filter(None, [ACTION_GATE_DIR, env.get("PYTHONPATH")]))
        payload = json.dumps(corpus)
        for seed in ("0", "1", "4242"):
            run = subprocess.run(
                [sys.executable, "-c", _REPLAY_CHILD, SECRET.decode()],
                input=payload, env={**env, "PYTHONHASHSEED": seed}, cwd=ACTION_GATE_DIR,
                capture_output=True, text=True, timeout=120,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout), expected, f"verdicts diverged under PYTHONHASHSEED={seed}")


# --------------------------------------------------------------------------- P5


class FourStateFailClosed(unittest.TestCase):
    NOT_EXECUTABLE = [
        "ASK", "SANDBOX", "DENY",
        "allow", "Allow", "ALLOW ", " ALLOW", "ALLOW\n", "ALLOWED", "PROCEED",
        "", "NONE", "ASK|ALLOW", "ALLOW" + chr(0x200B), None, True, 1, ["ALLOW"],
    ]

    def test_only_the_exact_string_allow_is_executable(self):
        self.assertEqual(verdict(issue(decision="ALLOW")), "ACCEPT")
        leaks = {}
        for state in self.NOT_EXECUTABLE:
            registry: set[str] = set()
            got = verdict(issue(decision=state), used_nonces=registry)
            if got != "decision_not_executable" or registry:
                leaks[repr(state)] = (got, sorted(registry))
        self.assertEqual(leaks, {})


# --------------------------------------------------------------------------- known gaps


class _InterleavingSet(set):
    """A nonce registry whose membership test lets a competing verifier catch up."""

    def __init__(self, parties: int) -> None:
        super().__init__()
        self._barrier = threading.Barrier(parties, timeout=3)

    def __contains__(self, item) -> bool:
        present = super().__contains__(item)  # every verifier observes 'unused'...
        try:
            self._barrier.wait()  # ...before any of them records the nonce
        except threading.BrokenBarrierError:
            pass
        return present


class KnownGaps(unittest.TestCase):
    @unittest.expectedFailure
    def test_gap_in_memory_nonce_registry_is_not_atomic(self):
        """GAP: verify_authority(used_nonces=...) is check-then-add. Two verifiers
        that interleave both accept the same single-use authority. The service
        path claims nonces in SQLite instead, so this is an API hazard, not a
        known service bug."""
        authority = issue()
        registry = _InterleavingSet(2)
        outcomes = race(2, lambda i: verdict(authority, used_nonces=registry))
        self.assertEqual(outcomes.count("ACCEPT"), 1, outcomes)

    @unittest.expectedFailure
    def test_gap_canonical_json_accepts_non_finite_numbers(self):
        """GAP: NaN / Infinity are not valid JSON, yet they are signed and hashed
        as if they were. Signed bytes should be portable across verifiers."""
        accepted = []
        for name, bad in (("nan", float("nan")), ("inf", float("inf")), ("-inf", float("-inf"))):
            try:
                canonical_json({"x": bad})
                accepted.append(name)
            except ValueError:
                pass
        self.assertEqual(accepted, [], "non-finite numbers were canonicalized")

    @unittest.expectedFailure
    def test_gap_ledger_accepts_duplicate_event_ids(self):
        """GAP: an append-only evidence ledger should refuse a second event that
        reuses an existing event_id."""
        ledger = EvidenceLedger()
        ledger.append("dup", "DECISION", "trace", {"a": 1})
        with self.assertRaises(Exception):
            ledger.append("dup", "EXECUTION", "trace", {"a": 2})

    @unittest.expectedFailure
    def test_gap_ledger_aliases_nested_payload_objects(self):
        """GAP: append() copies the payload one level deep. A caller that mutates
        a nested object afterwards silently changes stored evidence (the chain
        then fails verification)."""
        ledger = EvidenceLedger()
        payload = {"detail": {"amount": 1}}
        ledger.append("e1", "DECISION", "trace", payload)
        payload["detail"]["amount"] = 999
        self.assertTrue(ledger.verify_chain(), "caller mutation reached the stored event")

    @unittest.expectedFailure
    def test_gap_ledger_accepts_non_finite_numbers(self):
        """GAP: same portability problem as canonical_json, in the ledger hash."""
        ledger = EvidenceLedger()
        with self.assertRaises(ValueError):
            ledger.append("e1", "DECISION", "trace", {"x": float("nan")})


class KnownStorageGaps(StorageCase):
    @unittest.expectedFailure
    def test_gap_audit_events_can_be_overwritten_with_insert_or_replace(self):
        """GAP: the BEFORE UPDATE / BEFORE DELETE triggers do not fire for the
        delete that INSERT OR REPLACE performs while resolving a primary-key
        conflict (recursive triggers are off by default). storage.py itself only
        REPLACEs the records table, so exploiting this needs a SQL-capable writer."""
        _save(_record(1))
        with closing(sqlite3.connect(self.db_path, timeout=10)) as con:
            original = con.execute("SELECT * FROM audit_events").fetchone()
            forged = (original[0], original[1], original[2], '{"forged":true}', original[4], original[5], original[6])
            try:
                con.execute("INSERT OR REPLACE INTO audit_events VALUES (?,?,?,?,?,?,?)", forged)
                con.commit()
            except sqlite3.DatabaseError:
                con.rollback()
            after = con.execute("SELECT * FROM audit_events WHERE event_id=?", (original[0],)).fetchone()
        self.assertEqual(after, original, "an existing audit event was overwritten")


if __name__ == "__main__":
    unittest.main()
