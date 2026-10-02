# Architecture Status

## Chemical Reactivity Research Surface

| Signal | Emitted | Tested | Enforced | Authority effect |
|---|---|---|---|---|
| PROCEED | YES | YES | NO, requests Action Gate authorization | NONE |
| INHIBIT | YES | YES | Research-layer block only | NONE |
| HOLD | YES | YES | NO | NONE |
| UNKNOWN | YES | YES | NO | NONE |

PROCEED is deliberately non-authoritative. The chemical/state-bound layer cannot mint or consume execution authority.

HOLD and UNKNOWN currently have explicit consumer semantics: REQUIRE_REEVALUATION and REQUIRE_EVIDENCE. They have no Action Gate enforcement binding and must not be represented as execution controls until an execution-path test proves the binding.

## Version invariant

action_gate/VERSION is the canonical product-version source. PRODUCT/VERSION_SOURCES.json declares derived documents and the source classes covered by the version-source gate. The gate fails when a version-bearing tracked source is found outside that declaration.

## Verification discipline

A CI failure must be diagnosed from raw failing job output before a hypothesis or fix is proposed.

A signal without an enforcer is a tested signal, not an execution control.
