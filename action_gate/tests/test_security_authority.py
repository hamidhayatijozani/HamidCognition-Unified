import pytest

from action_gate.security_authority import (
    AuthorityError,
    issue_authority,
    verify_authority,
)


SECRET = b"test-only-action-gate-secret"
ACTION = {"verb": "write", "resource": "customer/42", "operation": "update"}
POLICY = {"version": "p1", "rule": "customer-write"}


def make(**kwargs):
    return issue_authority(
        secret=SECRET,
        decision_id="dec-1",
        tenant_id="tenant-a",
        action=ACTION,
        policy=POLICY,
        decision="ALLOW",
        now=1000,
        nonce="nonce-1",
        **kwargs,
    )


def test_valid_authority_is_accepted():
    verify_authority(
        authority=make(), secret=SECRET, tenant_id="tenant-a",
        action=ACTION, policy=POLICY, now=1001, used_nonces=set()
    )


def test_tampered_signature_is_denied():
    a = make()
    a = a.__class__(**{**a.__dict__, "signature": "0" * 64})
    with pytest.raises(AuthorityError, match="invalid_signature"):
        verify_authority(authority=a, secret=SECRET, tenant_id="tenant-a", action=ACTION, policy=POLICY, now=1001)


def test_action_binding_prevents_decision_reuse():
    with pytest.raises(AuthorityError, match="action_binding_mismatch"):
        verify_authority(authority=make(), secret=SECRET, tenant_id="tenant-a",
                         action={**ACTION, "resource": "customer/99"}, policy=POLICY, now=1001)


def test_tenant_isolation_prevents_cross_tenant_use():
    with pytest.raises(AuthorityError, match="tenant_mismatch"):
        verify_authority(authority=make(), secret=SECRET, tenant_id="tenant-b",
                         action=ACTION, policy=POLICY, now=1001)


def test_expired_authority_is_denied():
    with pytest.raises(AuthorityError, match="expired_or_not_yet_valid"):
        verify_authority(authority=make(ttl_seconds=5), secret=SECRET,
                         tenant_id="tenant-a", action=ACTION, policy=POLICY, now=1005)


def test_nonce_reuse_is_denied():
    used = set()
    a = make()
    verify_authority(authority=a, secret=SECRET, tenant_id="tenant-a",
                     action=ACTION, policy=POLICY, now=1001, used_nonces=used)
    with pytest.raises(AuthorityError, match="nonce_reuse"):
        verify_authority(authority=a, secret=SECRET, tenant_id="tenant-a",
                         action=ACTION, policy=POLICY, now=1002, used_nonces=used)


def test_non_executable_decision_cannot_be_authority():
    a = issue_authority(secret=SECRET, decision_id="dec-2", tenant_id="tenant-a",
                        action=ACTION, policy=POLICY, decision="ASK", now=1000, nonce="nonce-2")
    with pytest.raises(AuthorityError, match="decision_not_executable"):
        verify_authority(authority=a, secret=SECRET, tenant_id="tenant-a",
                         action=ACTION, policy=POLICY, now=1001)
