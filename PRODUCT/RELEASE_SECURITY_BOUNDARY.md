# Action Gate Release Security Boundary

This repository treats a release candidate as an evidence-bearing build, not merely a successful Docker build.

For a main-branch release candidate at commit SHA X, the release workflow is permitted to build an artifact only after successful runs for the same SHA of:

1. Action Gate Clean-Room Verification
2. Action Gate Product Integrity
3. Action Gate Production E2E Smoke
4. GitHub CodeQL (repository default setup)

The dependency is fail-closed: if a prerequisite is absent, cancelled, failed, or belongs to another SHA, the release candidate is blocked.

CodeQL is a detection layer supplied by the repository's GitHub CodeQL default setup. A successful CodeQL check proves that analysis completed for the exact SHA and, for pull-request analysis, that no new alert was reported in the changed code. It does not prove that the repository has zero historical findings. Open findings therefore remain visible in GitHub Code Scanning and are not silently converted into a "secure" claim by this repository.

Production E2E uses CI-only credentials and must not be interpreted as evidence of production secret quality or external infrastructure readiness.

The release artifact records the exact source SHA and prerequisite workflow run IDs so the artifact can be traced back to the evidence that authorized its construction.
