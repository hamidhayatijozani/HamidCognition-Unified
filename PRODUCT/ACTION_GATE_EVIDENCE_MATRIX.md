# Action Gate Evidence Matrix — Pre-Outreach

Date: 2026-10-08

| Capability | Evidence | Status |
|---|---|---|
| Canonical version | action_gate/VERSION | VERIFIED |
| Same-SHA release chain | PRODUCT/PRODUCT_COMPLETION_CONTROL.md + workflow 36966012148 | VERIFIED |
| Execution authority | action_gate/security_authority.py + SECURITY_AUTHORITY_GATE.md | VERIFIED IN CODE/EVIDENCE |
| Tenant/actor/session binding | CUSTOMER_ACCEPTANCE.md + authority contract | VERIFIED IN ACCEPTANCE CONTRACT |
| Action and policy binding | authority/action digest and policy digest checks | VERIFIED IN CODE/ACCEPTANCE CONTRACT |
| Expiry and nonce | CUSTOMER_ACCEPTANCE.md + action_gate/README.md | VERIFIED IN CODE/ACCEPTANCE CONTRACT |
| Replay protection | replay API + acceptance contract | VERIFIED IN CODE/EVIDENCE |
| HTTP enforcement | product boundary documentation | VERIFIED AS DOCUMENTED CAPABILITY |
| MCP enforcement | scripts/mcp_e2e_smoke.py + product docs | IMPLEMENTED; LIVE DEPLOYMENT NOT VERIFIED HERE |
| Direct downstream bypass resistance | threat model + acceptance suite | TESTED/DESIGNED; LIVE CUSTOMER DEPLOYMENT NOT VERIFIED |
| Fail-closed evidence handling | threat model + product controls | VERIFIED IN CODE/TEST CONTRACT |
| PostgreSQL persistence | product deployment boundary | VERIFIED AS PRODUCT CAPABILITY |
| Evidence retrieval/replay | MCP smoke path + replay API | IMPLEMENTED; LIVE EXTERNAL ENDPOINT NOT VERIFIED HERE |
| Anderson-style telemetry plane | no dedicated full flight-recorder telemetry plane located | GAP |
| Tripwires/honeytokens | no implementation located | GAP |
| Continuous anomaly detection | no demonstrated commercial detection plane located | GAP |
| Kill-switch control plane | DENY/SANDBOX/ASK exist; independent kill switch not established | PARTIAL |
| MCP server trust/supply chain | insufficient evidence | GAP |
| Business-impact intelligence | insufficient evidence | GAP |

## Evidence rule

Documentation is not execution proof. This matrix distinguishes implemented/documented capability from live deployment verification.

## Product conclusion

Action Gate has a strong execution-enforcement boundary. It must not be described as implementing the entire behavioral-detection and containment thesis associated with Anderson's work.
