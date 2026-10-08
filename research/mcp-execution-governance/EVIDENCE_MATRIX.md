# Evidence Matrix — MCP Execution Governance Study

**Status:** Initial inventory from repository records and product documentation, not an independent test report.

Evidence classes: **RELEASE RECORD** = release metadata; **DOC** = documentation claim; **LIVE EXPERIMENT** = controlled behavior test with raw evidence; **UNKNOWN** = evidence not yet collected or insufficient.

| Claim/control | Current evidence | Class | Status | Required next evidence |
|---|---|---|---|---|
| Published release v1.1.1 | `action_gate/VERSION`, `PRODUCT/COMMERCIAL_RELEASE.json`, `PRODUCT/RELEASE_TRUTH_RECORD.md` | RELEASE RECORD | Identified | Verify downloaded artifact embeds this version |
| Source commit `e9ea7565f4ddea91f5c45104237bd20564c80894` | Commercial release JSON and truth record | RELEASE RECORD | Recorded | Inspect matching workflow/run logs |
| Artifact SHA-256 `517064de0427286ff4f346d46996642aca3b9def891d1c08bfaebc25546fb791` | Commercial release JSON and truth record | RELEASE RECORD | Recorded, not recomputed in this study | Obtain bytes and independently hash |
| Tenant/actor/session/action binding | Product spec and handoff | DOC | UNKNOWN behaviorally | Context-mutation tests on pinned artifact |
| HTTP and MCP enforcement | Product spec | DOC | UNKNOWN behaviorally | Exercise real protected HTTP/MCP paths and inspect side effects |
| Single-use authority / nonce | Product spec and delivery manifest | DOC | UNKNOWN behaviorally | Sequential and concurrent replay, including restart |
| Expired authority rejection | Product spec and acceptance requirements | DOC | UNKNOWN behaviorally | Expiry-boundary tests |
| Fail-closed evidence handling | Product spec and handoff | DOC | UNKNOWN behaviorally | Inject evidence-store failure; inspect tool side effects |
| PostgreSQL persistence / restart replay | Product documentation | DOC | UNKNOWN behaviorally | Restart with persistent DB and retest |
| Action or policy tampering | Product documentation / Risk Lab plan | DOC | UNKNOWN behaviorally | Mutate action/policy after authorization |
| Direct downstream bypass | Risk Lab says rejection depends on enforcement configuration | DOC, conditional | UNKNOWN | Attempt bypass on actual test topology |
| Evidence retrieval and replay | Product documentation | DOC | UNKNOWN behaviorally | Independent replay and correlation with side-effect ledger |
| Atomic TOCTOU protection | Not established by files reviewed for this matrix | UNKNOWN | UNKNOWN | Inspect implementation; design concurrent TOCTOU test |
| Independent evidence plane | Not established by files reviewed | UNKNOWN | UNKNOWN | Architecture/code inspection |
| Continuous anomaly detection | Not established by files reviewed | UNKNOWN | UNKNOWN | Inspect code/config; do not claim without evidence |
| Tripwires / honeytokens | Not established by files reviewed | UNKNOWN | UNKNOWN | Inspect implementation and test or record gap |
| Kill switch / containment | Not established by files reviewed | UNKNOWN | UNKNOWN | Identify and test actual control or record gap |
| Customer acceptance / paid deployment | Release docs separate these from technical validation | DOC | NOT ESTABLISHED | External acceptance and transaction records |
| Revenue / customer ROI | No proof examined for this study | UNKNOWN | NOT ESTABLISHED | Verified transaction or measured customer outcome |

## Interpretation rules
1. A documented feature is not demonstrated behavior.
2. CI supports only tests that actually ran on its exact SHA.
3. A gateway rejection is insufficient if the downstream side effect occurred.
4. No percentage without numerator, denominator, and raw outcomes.
5. Unexecuted tests are UNKNOWN, not PASS.
6. Release provenance and experimental provenance must remain separate.