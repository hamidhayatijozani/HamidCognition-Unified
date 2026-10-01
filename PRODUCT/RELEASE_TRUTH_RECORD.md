# Release Truth Record

**Status:** AUTHORITATIVE REPOSITORY RECORD  
**Purpose:** Prevent misstatement of the Action Gate release state.

## Facts verified from GitHub

- **Historical technical release:** action-gate-v1.1.0
- **Release source commit:** 43e558deacbe3df06554f79178b922b27ac94b1a
- **Release Candidate workflow run:** 36309864630
- **Release Candidate artifact:** action-gate-release-candidate-1.1.0-43e558deacbe3df06554f79178b922b27ac94b1a
- **Artifact digest:** sha256:867aa038def640b77da9dd0057c948c7a6673b0e1388c6232802a92c4e05fd7c
- **Current main at record time:** c5a6f8a44a2a9b7ad6429fc51b24f6ceebeb946f

## Required interpretation

1. v1.1.0 is a VERIFIED HISTORICAL PUBLISHED TECHNICAL RELEASE.
2. main/c5a6f8a... is a later development HEAD, not the v1.1.0 release source.
3. The existence of later commits on main does NOT invalidate the historical v1.1.0 release.
4. The current main HEAD must NOT be described as the v1.1.0 release artifact or as a newly validated release without a new same-SHA evidence chain.
5. v1.1.0 commercial/customer validation is NOT VERIFIED by this record.
6. v1.0.10 remains the last independently validated/published commercial baseline unless a later same-SHA commercial validation record is added.
7. The v1.1.0 source commit 43e558de... is unsigned at the Git commit-signature level. It must not be described as cryptographically signed or signature-verified.
8. A release claim is verified only when the exact source SHA, workflow evidence, artifact digest, tests/evidence and release record refer to the same immutable source revision.

## Non-negotiable evidence rule

Never substitute:
- a moving main HEAD for the release SHA;
- a README or release note for executable evidence;
- a green workflow on another SHA for the release workflow;
- an artifact without its source SHA and digest;
- a historical release for current commercial/customer validation.

If any required link in the chain is missing, the claim is NOT VERIFIED, not “almost verified”.

## Canonical chain

SOURCE SHA → WORKFLOW → JOB → LOG → ARTIFACT → TEST/EVIDENCE → DIGEST → RELEASE

This record is a clarification of release provenance. It does not delete, rewrite, invalidate, or replace the existing v1.1.0 GitHub Release.
