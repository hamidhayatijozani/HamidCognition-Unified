# Action Gate Evidence Matrix — Pre-Outreach

**Audit date:** 2026-10-08  
**Rule:** a result supports only the scenario, source revision, environment and request path actually observed. Documentation and acceptance contracts are not equivalent to a fresh live execution.

| Claim / scenario | Evidence currently available | Status | Safe external wording | Remaining gap |
|---|---|---|---|---|
| Canonical version | `action_gate/VERSION` on main reads `1.1.1` | VERIFIED AS FILE CONTENT | “The canonical version file currently reads 1.1.1.” | Main SHA differs from published release SHA |
| Published release | Tag `action-gate-v1.1.1`; workflow `36966012148` success; release SHA `e9ea7565f4ddea91f5c45104237bd20564c80894`; artifact digest `517064de0427286ff4f346d46996642aca3b9def891d1c08bfaebc25546fb791` | OBSERVED | “A v1.1.1 artifact is published with a recorded source SHA and checksum.” | Does not validate later main commits |
| Execution authority | `action_gate/security_authority.py`, authority documentation and release/test records | IMPLEMENTED / DOCUMENTED | Describe the specific authority mechanism and tested version | Current main was not clean-room rerun in this audit |
| Tenant/actor/session binding | Authority contract and customer acceptance material | CONTRACT/CODE CLAIM; NOT CUSTOMER-DEPLOYMENT PROOF | “The design binds authority to action context.” | Need exact-SHA test output across all identity mutations |
| Action and policy binding | Action/policy digest checks documented in implementation and acceptance material | IMPLEMENTED; SCOPE-LIMITED EVIDENCE | “The tested path binds the request to action/policy digests.” | Need tampering scenarios recorded as fresh results |
| G01 governed authorized execution | Risk Lab source `tools/run_risk_lab_demo.py`; prior run `36429274558`; artifact digest `19141b22b0a17488dce982c2593ee66e6e2575dbe2a05f901df22d3a56929684` | RECORDED PASS | “The recorded Risk Lab run observed the authorized path succeed.” | Not independently rerun in this audit |
| G02 direct call to protected tool without authority | Same Risk Lab evidence reports HTTP 403 | RECORDED PASS | “In that run, a direct call to the protected endpoint without authority was rejected with HTTP 403.” | Limited to that implementation, setup and route |
| G03 reuse of same authority | Same Risk Lab evidence reports HTTP 403 on replay | RECORDED PASS | “In that run, reuse of the same authority was rejected with HTTP 403.” | Does not prove all replay/race/distributed cases |
| B01 baseline direct execution | Script creates a separate local `BaselineHandler` on port 9100 and labels it `baseline-unprotected-reference`; response HTTP 200 | INTENTIONAL BASELINE | “An unprotected reference endpoint executes as a baseline control.” | It is not evidence that the protected endpoint was bypassed |
| Expiry rejection | Listed in pilot acceptance scope, not demonstrated by G01–G03 script | UNKNOWN IN REVIEWED RUN | “Expiry is a planned customer acceptance test.” | Need run output and artifact |
| Tenant substitution/tampering | Acceptance scope/docs; no fresh result verified here | UNKNOWN IN REVIEWED RUN | “Tenant mutation is in the proposed test plan.” | Need raw request/response and result |
| Action/policy tampering | Acceptance scope/docs; no fresh result verified here | UNKNOWN IN REVIEWED RUN | “Action and policy mutation will be tested.” | Need exact-SHA evidence |
| Concurrent nonce race | Pilot scope only in evidence reviewed | UNKNOWN IN REVIEWED RUN | “Concurrency is a proposed acceptance case.” | Need reproducible parallel test |
| Restart/persistence | Deployment docs and pilot scope | NOT VERIFIED IN THIS AUDIT | “Restart/persistence is an acceptance gate.” | Need restart test with persisted state |
| HTTP/MCP parity | MCP E2E/smoke tooling and product docs exist | IMPLEMENTED; PARITY NOT RE-RUN HERE | “HTTP/MCP parity is a verification item for the selected deployment.” | Need same-SHA evidence across both paths |
| PostgreSQL persistence / fail-closed behavior | Product docs and implementation/test contracts | DOCUMENTED/IMPLEMENTED CLAIM | State only exact behaviors demonstrated by referenced tests | No customer deployment or current-main execution proved here |
| Customer acceptance / revenue | Issue #66 still tracks external gates; no customer transaction evidence reviewed | NOT OBSERVED | Do not claim customer validation, paid deployment or revenue | Requires external acceptance and transaction evidence |

## B01 interpretation

The inspected Risk Lab script starts two distinct paths:
- port 9100: disposable unprotected reference endpoint used as a baseline;
- port 9000: protected tool path exercised using Gate-issued execution authority.

Therefore B01 HTTP 200 is deliberate baseline behavior. G01–G03 describe the governed path. Do not market B01 as a Gate bypass defect.

## Evidence packet required for a customer test

1. Exact release tag, source SHA, artifact URL and SHA-256.
2. Exact test source commit, workflow URL, raw logs and artifact metadata.
3. Clear explanation of B01 versus G01–G03.
4. Customer-approved workflow, scope and safe test environment.
5. Raw request/response, identity/context, policy version, timestamps, tool side-effect observation and per-case result.
6. Expiry, action/policy tampering, tenant substitution, concurrent reuse, restart/persistence and alternate-route tests.
7. Explicit limitations and all failed/untested cases.

## Readiness gates

- [x] Published release and artifact digest observed.
- [x] Recorded narrow G01–G03 outcomes identified.
- [x] B01 correctly classified as separate unprotected reference.
- [ ] Independently rerun main at its exact SHA.
- [ ] Fresh evidence for expiry, tampering, tenant, race and restart.
- [ ] HTTP/MCP parity verified on one exact SHA.
- [ ] Customer acceptance and revenue (not required to start outreach; never imply they exist).

## Sources

- [Risk Lab source](../tools/run_risk_lab_demo.py)
- [Risk Lab workflow run](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/36429274558)
- [v1.1.1 release](https://github.com/hamidhayatijozani/HamidCognition-Unified/releases/tag/action-gate-v1.1.1)
- [Pilot offer](../SALES/PILOT_OFFER.md)
- [Commercial launch gates](https://github.com/hamidhayatijozani/HamidCognition-Unified/issues/66)
