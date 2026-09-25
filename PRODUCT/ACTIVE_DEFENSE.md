# Active Defense Signals

HamidCognition Action Gate treats the protected-tool boundary as both an
authorization enforcement point and a security-observation point.

## What is implemented

High-signal enforcement failures can be classified as structured security
signals, including invalid signatures, malformed authorities, nonce reuse,
tenant-binding failures, action-binding failures, and policy-binding failures.

The signal is telemetry. It is not itself a quarantine decision, IP blacklist,
or claim of attacker attribution.

## Why this boundary matters

A rejected request is useful security evidence when the rejection reason can be
correlated with the decision, tenant and execution context without exposing the
authority secret. This supports SIEM integration, incident investigation and
customer-specific response automation.

## Deliberate non-goals

The product does not generate fake executable authorities or honey nonces.
A decoy that resembles a valid bearer authority can create ambiguity in logs,
increase operational risk, and accidentally become an execution primitive.

The product also does not automatically blacklist an IP or tenant merely because
one enforcement failure occurred. Shared infrastructure, NAT, retries and
misconfiguration can make such attribution unreliable.

Automatic quarantine should be a separately configured response policy using
authenticated identity, rate/sequence evidence and customer-approved thresholds.

## Future extension

A production adapter can emit SecuritySignal.as_dict() to the customer's SIEM
or event bus. A future response engine may correlate repeated signals into a
quarantine recommendation or customer-approved enforcement action.

The differentiator is therefore observable, policy-driven active defense at
the execution boundary, not obscurity of protocol syntax.
