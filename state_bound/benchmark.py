from __future__ import annotations

from dataclasses import asdict
from .models import Decision, WorldState, digest
from .verifier import verify_authority


def baseline_action_only(*, authorized_action: dict, current_action: dict) -> bool:
    """Baseline: authorize when the requested action payload is unchanged."""
    return digest(authorized_action) == digest(current_action)


def run_case(name: str, authority, current_world: WorldState) -> dict:
    action = authority.action
    baseline_allow = baseline_action_only(
        authorized_action=action,
        current_action=action,
    )
    experimental = verify_authority(
        authority,
        action=action,
        current_world=current_world,
        consumed_nonces=set(),
    )
    return {
        "id": name,
        "baseline_allow": baseline_allow,
        "experimental_allow": experimental.executable,
        "false_allow_exposure": baseline_allow and not experimental.executable,
        "experimental_status": experimental.status,
        "reasons": list(experimental.reasons),
    }
