# External Evidence Witness

## Purpose

The Evidence Chain Integrity workflow proves the repository-local lineage:

`source SHA → executed verifier → evidence JSON → SHA-256`

That chain is useful but is not an independent witness when every object lives inside the same repository trust boundary.

For main-branch executions, the workflow therefore adds a **keyless Sigstore signature** to the canonical evidence JSON.

## External trust boundary

The witness path is:

`source SHA → evidence JSON → SHA-256 → GitHub Actions OIDC identity → Sigstore/Fulcio certificate → Rekor transparency log`

The signing workflow is identified as:

`https://github.com/hamidhayatijozani/HamidCognition-Unified/.github/workflows/evidence-chain-integrity.yml@refs/heads/main`

The OIDC issuer is:

`https://token.actions.githubusercontent.com`

The signed object is exactly:

`evidence/evidence-chain-integrity.json`

The workflow also stores the Sigstore bundle and its SHA-256 digest in the CI artifact.

## What this proves

A successful witness establishes that:

1. the exact evidence JSON was signed by a short-lived Sigstore certificate;
2. the certificate identity is bound to this repository's Evidence Chain Integrity workflow on `main`;
3. the signing event was submitted to the Sigstore transparency infrastructure;
4. the signed digest is cryptographically bound to the evidence JSON;
5. the evidence JSON itself contains the exact GitHub source SHA and workflow run metadata.

It does **not** prove that the underlying software is safe, correct, commercially successful, or independently audited. Humans remain remarkably inventive at confusing cryptographic integrity with truth.

## Private-repository constraint

GitHub Artifact Attestations are not used for this private repository. GitHub's current documentation states that Artifact Attestations for private repositories require GitHub Enterprise Cloud. The public Sigstore path is used instead so the transparency witness is outside the repository's storage boundary.

## Verification

A verifier can use the stored evidence JSON and Sigstore bundle with Sigstore tooling. The workflow itself performs an identity-constrained verification after signing, and the bundle contains the material required for later verification.

The expected signer identity is:

`https://github.com/hamidhayatijozani/HamidCognition-Unified/.github/workflows/evidence-chain-integrity.yml@refs/heads/main`

The expected issuer is:

`https://token.actions.githubusercontent.com`

The evidence SHA-256 remains independently checkable with standard `sha256sum`.

## Claim boundary

Before this workflow executes successfully on a main commit:

**EXTERNAL_WITNESS = NOT VERIFIED**

After a successful main execution containing the Sigstore signing, identity verification, bundle upload, and evidence digest:

**EXTERNAL_WITNESS = VERIFIED for that exact evidence object and workflow execution**

This witness does not retroactively attest historical v1.1.1 unless the v1.1.1 release evidence itself is separately signed and recorded. The immutable v1.1.1 release remains a historical release; current main evidence is a separate lineage.
