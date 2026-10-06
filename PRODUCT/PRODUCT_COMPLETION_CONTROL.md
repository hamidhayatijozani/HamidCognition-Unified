# Product Completion Control

This file is the execution control for turning HamidCognition-Unified into a coherent commercial product while preserving the research program.

## Canonical product

Current product boundary: **HamidCognition Action Gate**.

The executable product version is sourced from `action_gate/VERSION`.

**Current main development line:** v1.1.1.

**Latest independently validated and published commercial release:** v1.1.1, release tag `action-gate-v1.1.1`, source commit `e9ea7565f4ddea91f5c45104237bd20564c80894`.

The v1.1.1 release evidence is bound to the exact source revision above. The mutable `main` branch may move beyond that revision and therefore is not automatically equivalent to the immutable release.

For every mainline verification record, the evidence pack must state the **same source SHA** as `GITHUB_SHA`; a successful release record for an older commit does not satisfy this requirement.

## Completion gates

1. **Repository integrity**
   - one canonical main branch;
   - version references agree with `action_gate/VERSION`;
   - obsolete product claims are removed or explicitly marked historical;
   - provenance and rights records remain intact.

2. **Executable integrity**
   - Action Gate starts from the production definition;
   - authentication, tenant/actor/session binding, decision integrity, nonce protection and fail-closed behavior are executable;
   - HTTP and MCP enforcement use the same governed authority;
   - direct downstream bypass is rejected;
   - policy binding is independently verified at the protected tool boundary.

3. **Evidence integrity**
   - customer acceptance tests are executable;
   - CI records the exact commit and result;
   - release evidence is tied to the same source revision;
   - failed or unverified claims are not presented as verified.

4. **Commercial readiness**
   - SELF_HOSTED, MANAGED and ENTERPRISE boundaries are explicit;
   - deployment and acceptance instructions are complete;
   - customer-facing scope excludes unsupported guarantees;
   - a reproducible release artifact can be identified.

5. **Research portfolio**
   - every research line is classified as IMPLEMENTED, HYPOTHESIS, UNKNOWN, FALSIFIED or SUPERSEDED;
   - only evidence-backed candidates move toward productization;
   - opportunities outside the repository are evaluated separately.

## Verified v1.1.1 release evidence

The release-candidate workflow completed successfully for source commit `e9ea7565f4ddea91f5c45104237bd20564c80894`:

- workflow run: `36966012148`;
- release tag: `action-gate-v1.1.1`;
- release artifact: `action-gate-1.1.1.tar`;
- release artifact SHA-256: `517064de0427286ff4f346d46996642aca3b9def891d1c08bfaebc25546fb791`;
- release-candidate evidence artifact digest: `sha256:2e59173f96517cff0f02dc0e3ef88dc5ba6604c0eb3be3d46cb0c823168d127`;
- workflow result: success.

The workflow job explicitly checked out the validated revision, read the canonical version, validated the release baseline, built the production image, exported the image archive, generated SHA-256 evidence, created the release manifest, and uploaded release evidence.

## Mainline rule

A successful release run proves the tested release revision. It does **not** prove later commits on `main`.

Therefore:

```
RELEASE_VERIFIED(commit X)
≠
MAIN_VERIFIED(commit Y)
```

unless `X == Y` or a new verification chain proves `Y`.

## Documentation execution-gap rule

The repository treats **DOCUMENTATION_EXECUTION_GAP** as a failure hypothesis, not as a fact. It is considered falsified only when claims can be traced through:

```
SOURCE SHA
→ clean checkout
→ execution
→ real output
→ artifact
→ digest
→ independent reproduction
→ release record
```

No document may upgrade an unverified claim to VERIFIED merely by repeating it.

## Portfolio rule

Do not merge research into the commercial runtime merely because it is interesting. Promote a research line only when it provides a concrete capability, an executable test, reproducible evidence, and a defensible user problem.

## Commercial truth

Technical release evidence does not establish customer transaction, revenue, regulatory certification, universal AI safety, downstream correctness, or guaranteed business outcomes.

Commercial payment remains governed separately by `PRODUCT/USDT_PAYMENT_POLICY.md`.
