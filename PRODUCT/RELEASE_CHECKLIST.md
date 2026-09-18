# Action Gate Release Checklist

## Engineering

- [x] Canonical version updated.
- [x] Runtime tests pass.
- [x] Validation Boundary tests pass.
- [x] HTTP enforcement passes.
- [x] MCP enforcement passes.
- [x] Production container starts.
- [x] PostgreSQL persistence passes.
- [x] Replay/persistence checks pass.
- [x] Evidence artifact retained.
- [x] Artifact SHA256 recorded.

## Security

- [ ] No production secrets in repository.
- [ ] Signing material externally managed.
- [ ] Actor/session/tenant binding covered.
- [ ] Nonce single-use covered.
- [ ] Evidence failure is fail-closed.
- [ ] SANDBOX cannot cross the production execution boundary.
- [ ] Direct downstream bypass path is absent or blocked.

## Customer delivery

- [ ] Deployment contract delivered.
- [ ] Integration contract delivered.
- [ ] Environment template delivered.
- [ ] Operations runbook delivered.
- [ ] Customer acceptance procedure delivered.
- [ ] Release notes and provenance seal identify the exact baseline.

## Evidence rule

Do not mark a checkbox because a file exists. Mark it only when the corresponding behavior has executable evidence.

## Final release record

Record version, commit, workflow run IDs, artifact ID, artifact SHA256, acceptance result, known limitations, and rollback target.
