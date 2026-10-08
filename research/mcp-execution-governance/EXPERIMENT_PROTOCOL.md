# Experiment Protocol: Action Gate at an MCP Boundary

**Status:** Draft; no experiment is claimed as completed.

## Scope
Use a disposable test tenant, synthetic identities, and a non-production MCP server. Do not use production credentials or destructive tools. Pin the exact release artifact, source commit, configuration, policy, and harness version. If the artifact digest cannot be verified, mark the release prerequisite UNKNOWN and stop.

## Comparison
- Baseline: test harness or agent → protected tool.
- Governed: test harness or agent → Action Gate → protected tool.

Use identical scenario inputs. Verify downstream side effects independently of the gateway response. Retain raw requests/responses and sanitized logs.

## Scenarios
1. Authorized action (positive control).
2. Unauthorized action.
3. Expired authority.
4. Reuse of a consumed authority / replay.
5. Action payload mutation after authorization.
6. Tenant, actor, or session mismatch.
7. Policy-version/hash mismatch.
8. Required evidence store unavailable.
9. Restart followed by authority replay.
10. Concurrent duplicate execution attempts.
11. Direct downstream bypass using the actual test topology and credentials.
12. Independent reviewer reconstruction from exported evidence.

## Required outcomes
For each case record expected condition, observed gate result, downstream side-effect count, evidence identifier, timestamp, release/source identifier, and verdict. A DENY response is insufficient if the protected side effect still occurs.

Initial repeatability screen: 30 attempts per non-race scenario. Race tests should use 1, 2, 5, 10, and 25 concurrent duplicate requests where supported. These are proposed counts, not completed runs.

## Verdicts
- PASS: predefined acceptance condition observed with complete raw evidence.
- FAIL: acceptance condition violated.
- UNKNOWN: not run, setup unavailable, or evidence incomplete.
- NOT APPLICABLE: excluded with written rationale.

## Evidence bundle
Retain a manifest (source SHA, release tag, artifact digest, environment, configuration/policy hashes), scenario ledger, raw requests/responses, independent tool-side-effect ledger, replay output, file checksums, and limitations. Never store secrets in the repository.

## Stop conditions
Stop and report UNKNOWN if artifact digest mismatches, side effects cannot be observed independently, the test could touch production, or required configuration cannot be supplied safely. A setup failure is not a product pass or fail.