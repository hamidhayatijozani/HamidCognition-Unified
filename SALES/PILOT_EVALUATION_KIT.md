# BESAZ / Action Gate — Paid Pilot Evaluation Kit

**Status:** Proposal template; not evidence of a customer, signed agreement, deployment, or payment.  
**Product baseline:** Action Gate v1.1.1 (`action_gate/VERSION`).  
**Audience:** CTO, platform engineering, AI infrastructure, product security.

## 1. The offer

**30-day, one-tool governance pilot — proposed price: USD 2,500.**

The pilot tests one real agent-to-tool path in a customer-controlled environment. Scope is deliberately narrow: one agent identity, one protected tool/API, one agreed policy, one test tenant, and a jointly approved acceptance suite. Additional tools, production rollout, bespoke connectors, and 24/7 support require separate written scope.

This is a proposed commercial offer, not a quote accepted by any customer. Confirm taxes, payment terms, hosting, support window, data processing terms, and license with the buyer before signature.

## 2. Buyer problem

An agent can receive an ALLOW decision and then execute against a changed resource, substituted action, wrong tenant, or replayed authority unless the tool boundary independently checks the authorization context. The pilot measures whether Action Gate blocks the agreed failure cases at the protected-tool boundary and leaves evidence that the buyer can inspect.

## 3. Pilot boundary

### Included
- One customer-selected agent-to-tool path.
- One protected HTTP or MCP tool (choose one as the initial acceptance path; the second is an optional parity test).
- Agreed policy and identity/context fields.
- ALLOW and negative-path tests (DENY, stale context, expired/replayed authority, action or tenant substitution, and Gate/evidence unavailability).
- Evidence and replay export for the executed cases.
- One technical handover and a written result: ACCEPT, ACCEPT WITH EXCEPTIONS, or REJECT.

### Excluded unless separately agreed
- Claim of universal agent security, certification, zero risk, or prevention of every TOCTOU race.
- Atomicity between authorization and arbitrary external side effects when the protected system offers no conditional-write primitive.
- Multi-tenant managed hosting, custom integrations, production SLA, compliance/legal certification, or unrestricted support.
- Use of synthetic test outcomes as customer production evidence.

## 4. Acceptance protocol

Before testing, buyer and seller record the target source/version, deployment topology, tool boundary, test identities, policy, expected outcomes, and evidence location. Both parties sign off on the cases before running them.

| Case | Stimulus | Required result |
|---|---|---|
| A1 | Valid, current, correctly bound action | Tool executes once; decision and evidence are retrievable |
| A2 | Explicit DENY or non-executable decision | Tool side effect count remains zero |
| A3 | Change protected resource/world after authorization | Stale authority is rejected at tool boundary |
| A4 | Substitute tenant, actor, action, or bound policy field | Rejected; no side effect |
| A5 | Reuse the same single-use authority/nonce | At most one execution accepted |
| A6 | Gate/evidence lookup unavailable or malformed | Fail closed; no side effect |
| A7 | Restart the service and replay persisted decisions | Recorded verdicts match; missing records are reported as failures |
| A8 | Inspect evidence chain and replay output | Buyer can export and independently inspect the agreed fields |

**Acceptance rule:** all mandatory cases pass on the agreed target build; raw logs and machine-readable results are delivered; no unexplained false allow; and the buyer signs the result. Any exception is listed explicitly. A green CI run alone is not customer acceptance.

## 5. Delivery plan

- **Days 1–3 — Scope:** identify buyer owner, tool, threat cases, data boundaries, success criteria, and rollback.
- **Days 4–10 — Integrate:** deploy in the buyer-controlled test environment; connect one tool; record exact versions/configuration.
- **Days 11–20 — Test:** execute the frozen acceptance suite; retain raw logs, decision IDs, replay output, and failures.
- **Days 21–25 — Remediate:** fix in-scope defects and rerun affected cases against a recorded commit/image.
- **Days 26–30 — Decide:** deliver evidence pack, exceptions, operational notes, and signed acceptance/rejection decision.

Timeline assumes timely access to a test environment, a technical owner, and the agreed tool interface. Delays in those dependencies shift dates rather than silently shrinking the test.

## 6. Required customer inputs

- Named technical owner and decision-maker.
- Non-production environment and a test tool with observable side effects.
- Test identities and sanitized representative actions.
- Security/data-handling constraints and retention requirements.
- Agreed network access and secrets supplied through the customer's secret manager.
- Written approval of test cases and rollback plan.

Do not put real credentials, customer payloads, or secrets in issues, pull requests, CI logs, or this repository.

## 7. Evidence pack checklist

- [ ] Product version, source SHA, image digest, configuration fingerprint (secrets excluded)
- [ ] Environment/topology and tested boundary
- [ ] Frozen test-case list with expected outcomes
- [ ] Raw execution logs and machine-readable results
- [ ] Decision/evidence IDs and replay outputs
- [ ] Side-effect counter or equivalent independent observation
- [ ] Failure/exception list and retest evidence
- [ ] Buyer sign-off: ACCEPT / ACCEPT WITH EXCEPTIONS / REJECT

## 8. Demo sequence (10 minutes)

1. State the exact boundary: agent → Action Gate → protected tool.
2. Run one valid action and show the resulting decision and evidence.
3. Run a DENY case and show the protected tool was not invoked.
4. Authorize under world/context A, change to B, then attempt the old authority; show rejection.
5. Attempt a replay and show the second execution is rejected.
6. Open the evidence/replay output and show the identifiers and recorded results.
7. State limitations plainly: this demonstrates only the tested build, configuration, and boundary.

Never use a simulated screen or historical CI artifact as if it were a live customer deployment. Label recordings and fixtures.

## 9. Outbound message

**Subject:** 30-day evaluation of agent-to-tool execution controls

We are building BESAZ Action Gate, a control boundary that evaluates agent actions and requires the protected tool to validate the resulting execution authority. We are proposing a tightly scoped 30-day pilot around one agent and one tool.

The evaluation focuses on observable cases: stale context, action/tenant substitution, replayed authority, fail-closed behavior, and evidence/replay inspection. We agree on the acceptance tests up front and share the raw results, including failures. The proposed pilot fee is USD 2,500, subject to scope and written agreement.

If this maps to a current risk in your agent platform, the first step is a short technical scoping session with the engineer responsible for the protected tool.

## 10. Honest current-state boundary

Repository CI and automated integration tests are engineering evidence. They do not prove a customer's environment has been deployed, a buyer has accepted the result, a contract is signed, or revenue has been received. Keep those statuses UNKNOWN until independently documented. Do not describe the product as certified or risk-free.
