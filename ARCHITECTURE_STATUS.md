# Architecture Status

This document separates claims from implemented code and integration.

| Claimed capability | Implemented | Integration |
|---|---|---|
| Activation condition model | YES: state_bound/chemical_reactivity.py | Research layer |
| Inhibition / hard inhibitor | YES: state_bound/chemical_reaction_network.py | Research layer |
| Stability factors | YES: context/state/evidence/trajectory factors | Research layer |
| Reactivity calculation | YES: deterministic bounded calculation | Research layer |
| Catalyst as evidence modifier | YES | Research layer |
| Weakest-node control | YES | Research layer |
| Cascade pressure | YES | Research layer |
| Reaction environment snapshot | YES: state_bound/chemical_execution.py | Not yet product-authoritative |
| Reaction assessment | YES | Not yet product-authoritative |
| Post-reaction state mutation | NO | NOT INTEGRATED |
| State transition execution | NO | NOT INTEGRATED |
| Baseline-relative drift detection | NO | NOT INTEGRATED |
| Equilibrium model | NO | NOT IMPLEMENTED |
| Physical activation energy | NO | NOT CLAIMED |
| Action Gate consumption of reaction assessment | NO on this branch | BLOCKED until integration patch |
| Reaction layer execution authority | NO | Explicitly prohibited |
| Deterministic trace hash lock | PARTIAL | Requires canonical trace contract test |

## Rules

1. A term borrowed from chemistry is not a product capability until it has an executable implementation and a test.
2. A signal is not an architectural control until a named consumer reads it.
3. A digest named post_reaction must represent an actual post-transition state. Until then it is a reaction summary digest.
4. Reaction assessment is advisory. Action Gate remains the sole execution authority.
5. No novelty, safety, or scientific-validity claim is implied by this model.
