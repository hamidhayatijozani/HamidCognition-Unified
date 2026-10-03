# Architecture Status

## Pre-execution Policy Signals

| Signal | Emitted | Tested | Enforced | Authority effect |
|---|---|---|---|---|
| PROCEED | YES | YES | NO, requests Action Gate authorization | NONE |
| INHIBIT | YES | YES | YES, Action Gate maps it to DENY | Execution decision effect: DENY |
| HOLD | YES | YES | NO | NONE |
| UNKNOWN | YES | YES | NO | NONE |

PROCEED is deliberately non-authoritative: it never bypasses normal Action Gate policy. INHIBIT is consumed by Action Gate as an execution decision input and maps to DENY. The pre-execution/state-bound layer still cannot mint execution authority; Action Gate remains the only enforcer.

HOLD and UNKNOWN currently have explicit research consumer semantics: REQUIRE_REEVALUATION and REQUIRE_EVIDENCE. They are consumed by Action Gate as ASK, requiring further decision handling, but they do not grant execution authority.

## Version invariant

action_gate/VERSION is the canonical product-version source. PRODUCT/VERSION_SOURCES.json classifies derived files, while the version-source gate scans all tracked text files for semantic-version literals. The gate scans all tracked text, but only a version-like literal in product-version context is an undeclared source. CI/runtime environment literals are classified under env_metadata; historical records remain explicitly ignored.

## Verification discipline

A CI failure must be diagnosed from raw failing job output before a hypothesis or fix is proposed.

A signal without an enforcer is a tested signal, not an execution control.


## Verification environment status

- Local execution: NOT VERIFIED in the current ChatGPT runtime because outbound network access is unavailable and no repository working tree is mounted.
- Remote execution via the canonical `make gates-local` chain: REQUIRED and authoritative for this HEAD.
- If the remote canonical chain is GREEN for the exact HEAD, the local-execution gap is acceptable for this HEAD; it remains an environment limitation, not a claim of local execution.
- Action Gate consumes the research signal as a decision input. INHIBIT is enforced as DENY; PROCEED never grants authority; HOLD/UNKNOWN map to ASK. The research layer itself has no authority to execute.


## Release identity debt closure

Release source_commit is no longer parsed from customer-facing prose. The structured authority is PRODUCT/COMMERCIAL_RELEASE.json, and action_gate/VERSION remains the sole product-version source.

The prior parser compatibility path for prose source-commit strings is intentionally retired. Future release identity changes must update the structured record and its synchronized documents.

## Canonical gate execution

make gates-local is the canonical execution entry point. It now delegates to the sequential gates-timed chain, which records per-gate elapsed time and gate logs under evidence/gates-timing/.

The canonical GitHub Actions workflow executes make -n gates-local before execution and then runs make gates-local with a 30-minute workflow timeout. Timing output is uploaded as an artifact.

Commit-level local execution in this ChatGPT runtime remains unavailable because no repository working tree is mounted here. CI execution is therefore the execution evidence for this branch until a real local working tree is available.

## Research authority closure

docs: close INHIBIT binding claim; Action Gate consumes INHIBIT as DENY while the research layer cannot mint execution authority.
