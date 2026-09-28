from dataclasses import dataclass
import hmac
from .authority import Authority, AuthorityError, _sign
from .epistemic import EpistemicState
from .state import InvariantReport, WorldState, digest

@dataclass(frozen=True)
class VerificationResult:
    status: str
    reason: str
    invariants: InvariantReport
    authority_issued: bool = False
    verification_started_at: int = 0

    @property
    def executable(self):
        return self.status == "VALID"

def verify_authority(authority: Authority, *, current_world: WorldState, current_action, tenant_subject, secret, now=1000, consumed_nonces=None):
    verification_started_at = now
    if not current_world.freshness_valid(now):
        report = InvariantReport(False, False, False, False, False, False, False)
        return VerificationResult("HOLD", "current_world_stale", report, False, verification_started_at)
    if not hmac.compare_digest(_sign(authority.payload(), secret), authority.signature):
        raise AuthorityError("invalid_signature")
    fp = current_world.fingerprint()
    invariants = InvariantReport(
        action=digest(current_action) == authority.action_hash,
        context=fp["context"] == authority.context_hash,
        state=fp["state"] == authority.state_hash,
        evidence=fp["evidence"] == authority.evidence_hash,
        trajectory=fp["trajectory"] == authority.trajectory_hash,
        policy=fp["policy"] == authority.policy_hash,
        environment=fp["environment"] == authority.environment_hash,
    )
    if authority.subject != tenant_subject:
        return VerificationResult("INVALID", "subject_mismatch", invariants, False, verification_started_at)
    if authority.epistemic_state != EpistemicState.KNOWN.value:
        return VerificationResult("HOLD", "epistemic_state_not_known", invariants, False, verification_started_at)
    if now < authority.issued_at or now >= authority.expires_at:
        return VerificationResult("INVALID", "authority_expired_or_not_yet_valid", invariants, False, verification_started_at)
    if not invariants.valid:
        return VerificationResult("INVALID", "world_state_invariant_failed", invariants, False, verification_started_at)
    if consumed_nonces is not None and authority.nonce in consumed_nonces:
        return VerificationResult("INVALID", "replay_rejected", invariants, False, verification_started_at)
    return VerificationResult("VALID", "all_invariants_hold", invariants, True, verification_started_at)

def execute_once(authority, *, current_world, current_action, tenant_subject, secret, consumed_nonces, now=1000):
    result = verify_authority(authority, current_world=current_world, current_action=current_action, tenant_subject=tenant_subject, secret=secret, now=now, consumed_nonces=consumed_nonces)
    # Research boundary: verification and the caller's real side effect are not atomic.
    # A production adapter must use a transaction/CAS boundary or explicitly accept this residual TOCTOU.
    if result.executable:
        consumed_nonces.add(authority.nonce)
    return result
