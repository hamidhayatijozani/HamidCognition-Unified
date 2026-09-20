# HC-CSG NEXUS v2.0 — EPI-MESH Research Boundary

Status: RESEARCH-ONLY. This branch does not change the Action Gate production path.

## Purpose

NEXUS v2.0 explores three capabilities around the existing Action Gate:

1. distributed policy evaluation with an explicit Byzantine quorum model;
2. zero-knowledge attestation of a fixed, circuit-defined decision statement;
3. bounded online learning that proposes policy-weight changes without mutating the production policy automatically.

The existing Action Gate remains the enforcement authority. No NEXUS component may create a bypass around reservation, nonce protection, execution evidence, replay, or the existing worker-enforcement boundary.

## Claims that are deliberately not made

The supplied EPI-MESH proposal contains several claims that are stronger than its implementation:

- HMAC-SHA256 is not a zero-knowledge proof or a Pedersen commitment.
- A public `paramsHash` proves only that the prover supplied that hash. It does not prove that the hash corresponds to the real private parameters unless those parameters, or a circuit-verifiable commitment/preimage relation, are inside the circuit.
- Shamir Secret Sharing distributes a secret. It does not by itself provide Byzantine fault tolerance or consensus.
- The supplied adaptive-weight code is not Bayesian inference and has no posterior model.
- A fixed 120 ms proving time and <5 ms verification time are performance hypotheses until measured on a specified CPU, circuit size, proving key and workload.
- "No comparable industrial system exists" is not established by this branch and requires a documented market/technical survey.

## Corrected ZK boundary

The first circuit target should prove a narrow statement:

> Given a private fixed-point feature vector and private canonical parameter preimage, the committed parameter root equals the public parameter commitment, the fixed-point risk equation is satisfied, and the public verdict is the policy verdict for the public policy version.

The circuit must constrain every derived value. In Circom, witness-assignment operators such as `<--` must not be used as a substitute for constraints. Derived arithmetic belongs in constrained expressions (`<==`) or explicit quotient/remainder gadgets.

The circuit also needs:

- explicit range constraints for every fixed-point input;
- an exact fixed-point division rule;
- an explicit tool-class input if verdict selection depends on tool class;
- a constrained relation between the private parameter representation and `paramsHash`;
- a versioned policy digest so the verifier knows which policy was proven;
- deterministic public-input ordering;
- negative tests for altered inputs, verdicts, policy versions and parameter commitments.

## Adaptive-learning boundary

Online feedback is kept in shadow mode:

`telemetry -> posterior update -> proposed weights -> validation -> signed policy candidate -> explicit promotion`

Production policy is immutable for a running deployment unless a separately authenticated policy update is accepted. A bad downstream outcome must never silently rewrite the live safety policy.

## BFT boundary

The mesh protocol needs a real quorum specification before implementation:

- N nodes;
- f Byzantine nodes tolerated;
- quorum size;
- node identity and authenticated voting;
- proposal/view/round rules;
- equivocation handling;
- deterministic aggregation;
- timeout/recovery;
- key rotation and membership changes.

"Entropy consensus" is not treated as a protocol until these invariants are executable and tested.

## Promotion gates

NEXUS can be considered for production only after:

1. circuit compilation and trusted-setup provenance are reproducible;
2. witness/proof verification passes positive and adversarial negative suites;
3. proof-generation and verification latency are measured, not estimated;
4. parameter binding is cryptographically demonstrated;
5. mesh safety/liveness properties are tested under Byzantine faults;
6. adaptive learning cannot mutate the live policy without explicit authenticated promotion;
7. Action Gate's existing fail-closed enforcement path remains intact;
8. decision replay remains distinct from external-world-state replay.

Until then this branch is research evidence, not a replacement for Action Gate 1.0.1.
