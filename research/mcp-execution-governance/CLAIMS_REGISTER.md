# Claims Register and Publication Gates

**Current decision: NOT READY FOR PAID PUBLICATION AS A COMPLETED EMPIRICAL STUDY.** Protocol drafted; empirical evidence pending.

| ID | Proposed claim | Falsification condition | Status | Required evidence |
|---|---|---|---|---|
| C1 | Pinned Action Gate blocks unauthorized protected actions | Unauthorized scenario creates a downstream side effect | UNKNOWN | Controlled runs + independent tool ledger |
| C2 | Single-use authority prevents duplicate side effects | Reuse creates more than one side effect | UNKNOWN | Sequential and concurrent replay evidence |
| C3 | Context mutation invalidates authorization | Mutated tenant/actor/session/action is accepted and executes | UNKNOWN | Controlled mutation cases |
| C4 | Expired authority is rejected | Expired authority creates a side effect | UNKNOWN | Expiry-boundary evidence |
| C5 | Mandatory evidence failure prevents execution | Tool executes despite required evidence failure | UNKNOWN | Fault injection + side-effect ledger |
| C6 | Configured topology blocks direct bypass | Direct caller reaches protected side effect outside the gateway | UNKNOWN | Network/credential test |
| C7 | Evidence supports independent reconstruction | Reviewer cannot correlate decision, authority, and side effect | UNKNOWN | Independent replay |
| C8 | The research branch contains a bounded anomaly detector, tripwire control, and kill-switch containment path | CI run `37835599661` on SHA `8e4d4c019af7a43560617c2a756c33f1f22cdc7e` fails, or route-level controls do not block | PARTIAL / VERSION-SPECIFIC | Six security-plane tests passed, including kill-switch route blocking, tripwire route blocking, bounded anomaly detection, and tamper-evident evidence verification. This does not establish continuous commercial detection or downstream side-effect containment. |
| C9 | Product is customer-validated or revenue-generating | No verifiable acceptance/transaction record exists | NOT ESTABLISHED | Separate external records |

## Publication gates
1. Verify exact release tag, source commit, and artifact digest.
2. Freeze scenarios and acceptance conditions before running tests.
3. Retain raw inputs/outputs and independent downstream side-effect evidence.
4. Have a second run or independent reviewer reproduce core results.
5. Include failures, UNKNOWNs, exclusions, and limitations.
6. Map every abstract/conclusion claim to evidence; documentation alone cannot support an empirical claim.
7. Confirm ownership, licensing, and rights for any third-party code, logos, or proprietary artifacts reproduced.
8. Do not sell or submit this draft as a completed study before these gates pass.

## Potential deliverable after the gates pass
A bounded, version-specific report: “Adversarial Evaluation of Execution-Time Authorization for One MCP Workflow,” with protocol, environment, attack cases, results, limitations, and a reproducible evidence capsule. It must not imply that every MCP deployment or AI agent is covered.