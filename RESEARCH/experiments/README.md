# Executable Research Experiments

These experiments are deliberately separated from product claims.

## STI-001

`sti_001.py` generates synthetic trajectories with independently specified failure labels and compares:

- outcome-only evaluation;
- confidence-only evaluation;
- provenance-only evaluation;
- explicit transition-integrity evaluation.

Run:

    python RESEARCH/experiments/sti_001.py --seed 20260924 --repetitions 10 --output sti001-result.json

The output contains the dataset fingerprint, aggregate rates, and detection rate by failure type.

Important boundary: a synthetic benchmark can test whether the representation distinguishes constructed failure modes. It cannot establish general intelligence, real-world validity, novelty, or historical priority.
