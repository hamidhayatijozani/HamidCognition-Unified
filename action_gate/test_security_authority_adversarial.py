"""Focused adversarial tests for signed execution-authority primitives.

These are unit-level checks. They do not substitute for database concurrency,
service-restart, or live HTTP/MCP integration evidence.
"""
from dataclasses import replace

import pytest

from security_authority import (
    AuthorityError,
    issue_authority,
    verify_authority,
)

SECRET = b"issue66-ci-authority-secret"
ACTION = {"action": "read_public_file", "target": "/public/info.txt"}
POLICY = {"version": "test-policy-v1", "decision": "ALLOW"}


def make_authority(**kwargs):
    defaults = {
        "secret": SECRET,
        "decision_id": "issue66-decision-1",
        "tenant_id": "tenant-a",
        "action": ACTION,
        "policy": POLICY,
        "decision": "ALLOW",
        "ttl_seconds": 60,
        "now": 1_000,
        "nonce": "issue66-single-use-nonce",
    }
    defaults.update(kwargs)
    return issue_authority(**defaults)


def test_expired_authority_is_rejected():
    authority = make_authority()
    with pytest.raises(AuthorityError, match="expired_or_not_yet_valid"):
        verify_authority(
            authority=authority, secret=SECRET, tenant_id="tenant-a",
            action=ACTION, policy=POLICY, now=1_060,
        )


def test_tenant_substitution_is_rejected():
    authority = make_authority()
    with pytest.raises(AuthorityError, match="tenant_mismatch"):
        verify_authority(
            authority=authority, secret=SECRET, tenant_id="tenant-b",
            action=ACTION, policy=POLICY, now=1_001,
        )


def test_action_and_policy_mutation_are_rejected():
    authority = make_authority()
    with pytest.raises(AuthorityError, match="action_binding_mismatch"):
        verify_authority(
            authority=authority, secret=SECRET, tenant_id="tenant-a",
            action={"action": "write_file", "target": "/public/info.txt"},
            policy=POLICY, now=1_001,
        )
    with pytest.raises(AuthorityError, match="policy_binding_mismatch"):
        verify_authority(
            authority=authority, secret=SECRET, tenant_id="tenant-a",
            action=ACTION, policy={"version": "mutated", "decision": "ALLOW"},
            now=1_001,
        )


def test_signature_tampering_is_rejected():
    authority = make_authority()
    tampered = replace(authority, signature="0" * 64)
    with pytest.raises(AuthorityError, match="invalid_signature"):
        verify_authority(
            authority=tampered, secret=SECRET, tenant_id="tenant-a",
            action=ACTION, policy=POLICY, now=1_001,
        )


def test_reuse_is_rejected_when_nonce_registry_is_supplied():
    authority = make_authority()
    used_nonces = set()
    verify_authority(
        authority=authority, secret=SECRET, tenant_id="tenant-a",
        action=ACTION, policy=POLICY, now=1_001, used_nonces=used_nonces,
    )
    with pytest.raises(AuthorityError, match="nonce_reuse"):
        verify_authority(
            authority=authority, secret=SECRET, tenant_id="tenant-a",
            action=ACTION, policy=POLICY, now=1_001, used_nonces=used_nonces,
        )
