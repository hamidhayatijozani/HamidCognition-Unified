# SIMORGH Agent: task intake bootstrap

## Scope of this increment

This is the first safe, phone-operable increment of the proposed SIMORGH agent system. It establishes an issue-as-command contract and validates requests. **It does not yet generate patches, run repository tests, push branches, or open PRs automatically.** Those actions require a separately configured model/runtime and narrowly scoped credentials; pretending an intake workflow is a coding agent would be fiction.

## Command flow

1. Open an issue in this repository.
2. Put a single JSON object in the issue body using `agent/task.schema.json`.
3. Apply the `simorgh:task` label.
4. `.github/workflows/simorgh-task-intake.yml` validates the contract and posts a receipt comment.
5. An authorized runner can later consume validated tasks and return patch/test evidence.

## Task example

```json
{
  "task": "Fix the failing DRS normalized-bounds test",
  "repo": "hamidhayatijozani/HamidCognition-Unified",
  "target": "kirgande/void_key.py",
  "acceptance": [
    "calculate_drs(1, 1, 1, 1) returns 1.0",
    "calculate_drs(0, 0, 0, 0) returns 0.0",
    "targeted tests pass"
  ]
}
```

## Safety invariants for the future runner

- Never execute arbitrary shell commands supplied by an issue.
- Allowlist repositories and permitted paths.
- Use a short-lived GitHub App installation token with contents:write and pull_requests:write only when creating a patch/PR.
- Run untrusted tests without production secrets.
- Never auto-merge or deploy from issue text.
- Record task ID, base SHA, patch SHA, test command, exit code, and workflow run URL.
- A green intake check is not proof of code correctness or a live runtime attachment.

## Current status

Stage 1 = issue contract validation. Stage 2 = isolated patch-generation runner. Stage 3 = test/evidence/PR loop. Stage 4 = live integration verification. Only Stage 1 is implemented by this bootstrap.
