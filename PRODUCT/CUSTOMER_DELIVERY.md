# Customer Delivery Procedure

## Purpose

This document defines the reproducible handoff path for an Action Gate customer delivery.

## Release identity

Use the exact commercial release, not the mutable main branch.

Current offerable release: **v1.0.10**  
Tag: `action-gate-v1.0.10`  
Source commit: `77d820e99dc78a6a9e3217d3c1c49d5cdf07813f`  
Artifact SHA-256: `10bb53b69b56ff86146f5c71e3e5d7e34dacb4e12dba2adafc59f9d5276abd91`

## Handoff sequence

1. Quote the exact product version.
2. Identify the release tag and source commit.
3. Provide the versioned artifact and checksum.
4. Select the delivery model: SELF_HOSTED, MANAGED, or ENTERPRISE.
5. Apply the applicable proprietary license and deployment scope.
6. Run the customer acceptance procedure against the customer's deployment.
7. Record acceptance evidence.
8. Settle payment under the configured payment policy.
9. Record the transaction hash and entitlement.
10. Preserve the final delivery record with the exact release identity.

## Important boundary

CI evidence demonstrates technical release evidence. It does not by itself demonstrate a customer sale, customer acceptance, payment settlement, regulatory certification, or downstream business correctness.

## Intellectual property

Copyright © 2026 Hamid Hayati Jozani. All rights reserved.

The repository is publicly visible, but the Action Gate product is proprietary unless a separate written license expressly grants other rights. Third-party components remain subject to their own licenses.

## Customer proof-of-value

The recommended technical scope is one high-impact agent tool or MCP server. The acceptance result should demonstrate the actual governed path from agent request through Action Gate to the protected tool and the resulting evidence.
