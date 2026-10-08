# Evidence Matrix — MCP Execution Governance Study

**Status:** Initial inventory from repository records and product documentation, not an independent test report.

Evidence classes: **RELEASE RECORD** = release metadata; **DOC** = documentation claim; **LIVE EXPERIMENT** = controlled behavior test with raw evidence; **UNKNOWN** = evidence not yet collected or insufficient.

| Claim/control | Current evidence | Class | Status | Required next evidence |
|---|---|---|---|---|
| Published release v1.1.1 | `action_gate/VERSION`, `PRODUCT/COMMERCIAL_RELEASE.json`, `PRODUCT/RELEASE_TRUTH_RECORD.md` | RELEASE RECORD | Identified | Verify downloaded artifact embeds this version |
| Source commit `e9ea7565f4ddea91f5c45104237bd20564c80894` | Commercial release JSON and truth record | RELEASE RECORD | Recorded | Inspect matching workflow/run logs |
| Artifact SHA-256 `517064de0427286ff4f346d46996642aca3b9def891d1c08bfaebc25546fb791` | Commercial release JSON and truth record | RELEASE RECORD | Recorded, not recomputed in this study | Obtain bytes and independently hash |
| Existing pre-outreach matrix | `PRODUCT/ACTION_GATE_EVIDENCE_MATRIX.md` | DOC | Useful index, not a substitute for this study's raw evidence | Trace every VERIFIED label to exact test/run and release SHA |
| Existing adversarial test definition | `PRODUCT/ANDERSON_EXECUTION_BOUNDARY_CHALLENGE.md` | DOC | Test definition ready; external workflow/customer deployment not verified | Execute on a pinned test deployment and retain side-effect evidence |
| Tenant/actor/session/action binding | Product spec and handoff | DOC | UNKNOWN behaviorally for this study | Context-mutation tests on pinned artifact |
| HTTP and MCP enforcement | Product spec and `scripts/mcp_e2e_smoke.py` | DOC / implementation pointer | UNKNOWN behaviorally for this study | Run against pinned release and inspect side effects |
| Single-use authority / nonce | Product spec and customer acceptance procedure | DOC | UNKNOWN behaviorally for this study | Sequential and concurrent replay, including restart |
| Expired authority rejection | Customer acceptance procedure | DOC | UNKNOWN behaviorally for this study | Expiry-boundary tests |
| Fail-closed evidence handling | Product spec and handoff | DOC | UNKNOWN behaviorally for this study | Inject evidence-store failure; inspect tool side effects |
| PostgreSQL persistence / restart replay | Product documentation | DOC | UNKNOWN behaviorally for this study | Restart with persistent DB and retest |
| Action or policy tampering | Product documentation / challenge plan | DOC | UNKNOWN behaviorally for this study | Mutate action/policy after authorization |
| Direct downstream bypass | Risk Lab says rejection depends on enforcement configuration | DOC, conditional | UNKNOWN | Attempt bypass on actual test topology |
| Evidence retrieval and replay | Product documentation and replay API references | DOC | UNKNOWN behaviorally | Independent replay and correlation with side-effect ledger |
| Atomic TOCTOU protection | Customer acceptance describes concurrent atomic nonce consumption; other authority-gate documentation describes concurrency as a future hardening item | CONFLICTING DOC SIGNALS | UNKNOWN / VERSION-DRIFT RISK | Inspect exact v1.1.1 source and run concurrent single-use test |
| Durable nonce state | Product handoff describes persistent PostgreSQL nonce storage; `action_gate/SECURITY_AUTHORITY_GATE.md` says process-local nonce state must be replaced by durable transactional storage | CONFLICTING DOC SIGNALS | UNKNOWN / VERSION-DRIFT RISK | Resolve against exact release source and runtime configuration before making a claim |
| Independent evidence plane | Existing pre-outreach matrix says no dedicated full flight-recorder plane located | DOC | GAP in current evidence | Architecture/code inspection; identify independent source of truth or state gap |
| Continuous anomaly detection | Existing pre-outreach matrix says no demonstrated commercial detection plane located | DOC | GAP in current evidence | Inspect code/config; do not claim without evidence |
| Tripwires / honeytokens | Existing pre-outreach matrix says no implementation located | DOC | GAP in current evidence | Inspect implementation and test or record gap |
| Kill switch / containment | Existing pre-outreach matrix says DENY/SANDBOX/ASK exist but independent kill switch is not established | DOC | PARTIAL / UNKNOWN | Identify and test actual containment control or record gap |
| Customer acceptance / paid deployment | Release docs separate these from technical validation | DOC | NOT ESTABLISHED | External acceptance and transaction records |
| Revenue / customer ROI | No proof examined for this study | UNKNOWN | NOT ESTABLISHED | Verified transaction or measured customer outcome |

## Interpretation rules
1. A documented feature is not demonstrated behavior.
2. CI supports only tests that actually ran on its exact SHA.
3. A gateway rejection is insufficient if the downstream side effect occurred.
4. No percentage without numerator, denominator, and raw outcomes.
5. Unexecuted tests are UNKNOWN, not PASS.
6. Release provenance and experimental provenance must remain separate.
7. Conflicting versioned documentation is a blocker until reconciled against the exact release source.