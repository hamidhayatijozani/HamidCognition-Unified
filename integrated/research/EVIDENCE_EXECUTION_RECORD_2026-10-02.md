# P/S/T Shock Recovery v1.1 — Execution Record

Execution date: 2026-10-02

## Source binding

The research implementation inspected on `main` was bound to commit:

`25531ba3b482e065cf55cd3ea2b66880e7377f07`

Files executed from that source:

- `integrated/research/shock_recovery.py`
- `integrated/research/test_integrated_shock_recovery.py`

## Reproduction result

The five falsification tests were reproduced locally from the exact fetched source content:

`5 passed in 0.05s`

Observed values:

- no-shock final T: `0.5`
- shock degradation T: `0.3181818182`
- persistent-shock final T: `0.01`
- shock-removal final T: `0.8`
- persistent-shock recovery gates: all `0`
- recovery trajectory: monotonic after shock removal

Replay SHA-256:

`4f4e0a6e314d8ef19b2a15ae2345e4beb7f3a9a330f7577189ec91b65a8e33fd`

## Important evidence boundary

This record proves deterministic local execution of the fetched source.

It is **not** a GitHub Actions attestation. The GitHub-hosted runner path must produce its own successful run and artifact before the result is labeled CI-verified.

## CI correction

The research workflow previously referenced the nonexistent `test_shock_recovery.py` path and only triggered on `research/shock-recovery-v1.1`.

The proof branch changes the workflow to execute:

`python -m pytest -q integrated/research/test_integrated_shock_recovery.py`

from repository root, and makes the evidence generator importable from that root.

No change is made to the Canonical P/S/T engine or the commercial Action Gate.
