# Architecture Status

This document separates claims from implemented code and integration. Every implemented/integrated claim names an executable artifact or test.

| Capability | Implemented | Integration / enforcement |
|---|---|---|
| Activation condition model | YES: state_bound/chemical_reactivity.py | state_bound/test_chemical_reactivity.py |
| Inhibition / hard inhibitor | YES: state_bound/chemical_reaction_network.py | state_bound/test_chemical_reaction_network.py |
| Stability factors | YES: state_bound/chemical_execution.py | state_bound/test_chemical_execution.py |
| Reactivity calculation | YES: deterministic bounded calculation | state_bound/test_chemical_reaction_network.py |
| Catalyst as evidence modifier | YES | state_bound/test_chemical_reaction_network.py |
| Weakest-node control | YES | state_bound/test_chemical_reaction_network.py |
| Cascade pressure | YES | state_bound/test_chemical_reaction_network.py |
| Reaction environment snapshot | YES: state_bound/chemical_execution.py | typed input from ActionRequest in action_gate/app.py |
| Typed Reaction Assessment interface | YES: state_bound/reaction_capability.py | ReactionPolicyInput consumed by Action Gate |
| Action Gate consumption of reaction assessment | YES | /v1/action/evaluate stores reaction_assessment in decision record |
| INHIBIT policy | YES: binding by default | INHIBIT maps to DENY unless explicit override reason is supplied and audited |
| INHIBIT override audit | YES | decision record reaction_policy + policy_checks; replay re-evaluates reaction |
| Reaction layer execution authority | NO | import boundary test + no execution methods |
| One-way import boundary | YES | state_bound/test_import_boundary.py; reaction layer cannot import action_gate.* |
| Canonical reaction trace digest | YES | state_bound/chemical_reaction_network.py + locked hash test |
| Reaction summary digest | YES | state_bound/chemical_execution.py; explicitly not a post-state digest |
| Post-reaction state mutation | NO | NOT INTEGRATED |
| State transition execution | NO | NOT INTEGRATED |
| Baseline-relative drift detection | NO | NOT INTEGRATED |
| Equilibrium model | NO | NOT IMPLEMENTED |
| Physical activation energy | NO | NOT CLAIMED |

## Policy contract

1. Reaction assessment is a typed input to Action Gate, not an execution authority.
2. INHIBIT is binding by default and produces DENY.
3. An INHIBIT override requires a non-empty explicit reason and is recorded in the signed decision evidence path.
4. HOLD and UNKNOWN remain advisory in this integration and do not independently authorize or deny execution.
5. Action Gate remains the sole execution authority.
6. No chemistry term is treated as a physical measurement, novelty proof, safety proof, or scientific claim.
7. No digest is called post-reaction until an actual post-transition state is observed and hashed.
8. The import boundary is enforced by test: reaction-layer modules must not import action_gate.*.
