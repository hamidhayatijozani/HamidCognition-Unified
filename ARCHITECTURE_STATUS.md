# Architecture Status

## Chemical Reactivity Research Surface

| Signal | Emitted | Tested | Enforced | Authority effect |
|---|---|---|---|---|
| PROCEED | YES | YES | NO, requests Action Gate authorization | NONE |
| INHIBIT | YES | YES | NO, research-layer advisory block only | NONE |
| HOLD | YES | YES | NO | NONE |
| UNKNOWN | YES | YES | NO | NONE |

PROCEED is deliberately non-authoritative. INHIBIT is advisory at the research boundary only: it blocks reaction progression inside the research model, but does not produce an Action Gate DENY or execution authority. The chemical/state-bound layer cannot mint execution authority.

HOLD and UNKNOWN currently have explicit consumer semantics: REQUIRE_REEVALUATION and REQUIRE_EVIDENCE. They have no Action Gate enforcement binding and must not be represented as execution controls until an execution-path test proves the binding.

## Version invariant

action_gate/VERSION is the canonical product-version source. PRODUCT/VERSION_SOURCES.json classifies derived files, while the version-source gate scans all tracked text files for semantic-version literals. Any tracked text file containing such a literal must be classified as derived or the gate fails.

## Verification discipline

A CI failure must be diagnosed from raw failing job output before a hypothesis or fix is proposed.

A signal without an enforcer is a tested signal, not an execution control.


## Verification environment status

- Local execution: NOT VERIFIED in the current ChatGPT runtime because outbound network access is unavailable and no repository working tree is mounted.
- Remote execution via the canonical `make gates-local` chain: REQUIRED and authoritative for this HEAD.
- If the remote canonical chain is GREEN for the exact HEAD, the local-execution gap is acceptable for this HEAD; it remains an environment limitation, not a claim of local execution.
- Action Gate signals: authority = NONE for all four research signals. INHIBIT blocks only within the research layer.
