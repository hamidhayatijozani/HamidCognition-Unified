# Theoretical Foundation: Persistent State and Adaptive Systems

This document is a set of hypotheses, not a claim that a new intelligence has been born.

## State
A practical stateful system can be represented as:
`M_t = g(X_t, M_{t-1}, \theta_t)`
where `X_t` is current input, `M_t` is explicitly stored state, and `\theta_t` is a versioned parameter set. Persistence requires a storage and retention design; it does not follow merely from a conversation or a model name.

## Adaptation
`\theta_t = update(\theta_{t-1}, D_{train}, objective)`
Any adaptive update must be reproducible, bounded, versioned, and evaluated on data not used for tuning. Changes to executable policy require review and rollback.

## Claims requiring evidence
- Better out-of-sample performance than baselines after costs.
- Stable replay of decisions from frozen inputs and versions.
- Lower false-allow rates under adversarial tests.
- Reliable operation after restart and partial failures.

Terms such as “independent superintelligence”, “alignment death”, and “infinite energy” are narrative labels, not validated technical results.
