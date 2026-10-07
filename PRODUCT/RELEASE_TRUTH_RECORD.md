# Release Truth Record

**Status:** AUTHORITATIVE REPOSITORY RECORD  
**Purpose:** Prevent misstatement of the Action Gate release state.

## Facts verified from GitHub

- **Current published technical release:** action-gate-v1.1.1
- **Release source commit:** e9ea7565f4ddea91f5c45104237bd20564c80894
- **Release Candidate workflow run:** 36966012148
- **Published tarball digest:** sha256:517064de0427286ff4f346d46996642aca3b9def891d1c08bfaebc25546fb791
- **Publisher:** github-actions[bot]
- **Current main is a later development line:** this record must not treat a moving main HEAD as the immutable release artifact.

## Required interpretation

1. v1.1.1 is the current VERIFIED PUBLISHED TECHNICAL RELEASE.
2. main is a later development HEAD, not the v1.1.1 release source.
3. The existence of later commits on main does NOT invalidate the immutable v1.1.1 release.
4. The current main HEAD must NOT be described as the v1.1.1 release artifact or as a newly validated release without a new same-SHA evidence chain.
5. v1.1.1 technical release validation is verified; customer acceptance remains deployment-specific and is NOT established by this record.
6. v1.1.1 is the current published product release; customer transaction, acceptance, payment and production deployment remain separate evidence.
7. The v1.1.1 release publisher is github-actions[bot]; do not infer Git commit-signature verification from publisher identity.
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

This record is a clarification of release provenance. It does not delete, rewrite, invalidate, or replace the existing v1.1.1 GitHub Release.
