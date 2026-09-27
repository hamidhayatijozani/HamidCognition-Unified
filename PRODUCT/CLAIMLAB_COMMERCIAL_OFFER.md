# ClaimLab — Commercial Sale Offer

Status: DRAFT / COMMERCIAL NEGOTIATION
Owner: Hamid Hayati Jozani
Product: HamidCognition Action Gate
Scope: one-time product sale plus recurring contractual payment

## Purpose

This ClaimLab separates verified product facts from commercial assertions and proposed deal terms. It is the evidence boundary for any buyer-facing statement about the proposed sale.

## Claim register

| ID | Claim | Type | Evidence required | Current status | Buyer-safe wording |
|---|---|---|---|---|---|
| CL-COM-001 | HamidCognition Action Gate has an implemented runtime with HTTP and MCP enforcement, decision evidence/replay, production authentication, fail-closed execution boundary, persistent PostgreSQL storage, execution-authority nonce state, production Compose deployment, and validation/clean-room evidence. | Observation | Current release source + same-SHA gates + release artifact | SUPPORTED BY CURRENT PRODUCT READINESS DOCUMENTATION; RE-VERIFY AT SALE SHA | The product includes the documented enforcement, persistence, replay, authentication and evidence capabilities, subject to acceptance testing. |
| CL-COM-002 | The product has passed the latest recorded Product Gates run on commit 0c407d52e9500d70e63bb385fc28b457f8c026b0. | Observation | GitHub Actions run 36283962383 and artifact action-gate-validation-evidence-36283962383 | VERIFIED FOR THAT COMMIT | The cited candidate commit passed the recorded Product Gates run. |
| CL-COM-003 | The validation evidence artifact for that run has SHA-256 0788a0b2da537c501aeb7acbcec7f8782dbe737136aaae845ea6749826214092. | Observation | GitHub Actions artifact metadata | VERIFIED | The validation evidence pack has the recorded SHA-256 digest. |
| CL-COM-004 | A one-time sale price of 3 BTC is the proposed commercial offer. | Commercial proposal | Executed quotation/contract | PROPOSED, NOT MARKET-VERIFIED | Proposed purchase price: 3 BTC. |
| CL-COM-005 | An additional payment of USD 100,000 is proposed for 1 August of each contract year. | Commercial proposal | Executed quotation/contract defining term, duration and consideration | PROPOSED, NOT CONTRACTED | Proposed annual payment: USD 100,000 due each 1 August during the agreed term. |
| CL-COM-006 | BTC or USDT may be used as settlement rails if the parties agree the conversion method, network, confirmation rule and receiving address. | Commercial/payment term | Final contract + payment instructions | PROPOSED | Settlement may be made in BTC or USDT under the agreed payment instructions. |
| CL-COM-007 | LiteFinance account identifier MT5-CLS-1205416 is the seller's intended receiving account reference. | Payment operational detail | Seller-controlled account verification | USER-PROVIDED; NOT AN ON-CHAIN ADDRESS | Payment destination will be the seller's verified payment details supplied at invoicing. |
| CL-COM-008 | The repository does not itself prove that a buyer exists, that the product has been sold, or that any payment has been received. | Boundary | GitHub repository and transaction records | VERIFIED BOUNDARY | Never claim a completed sale until signed agreement and settlement evidence exist. |
| CL-COM-009 | The commercial offer does not by itself transfer all intellectual-property rights. | Legal boundary | Final IP assignment/license clause | REQUIRED CONTRACTUAL DEFINITION | IP ownership and license scope are defined only by the executed agreement. |
| CL-COM-010 | No guaranteed ROI, universal safety outcome, regulatory certification, or downstream-tool correctness is included merely by making this offer. | Boundary | Product commercial-readiness boundary | SUPPORTED | Do not use outcome guarantees in sales material. |

## Commercial offer

### Proposed transaction

**One-time purchase consideration:** 3 BTC.

**Recurring consideration:** USD 100,000 payable on 1 August of each agreed contract year.

**Settlement rails:** BTC or USDT, subject to the executed payment schedule and verified payment instructions.

**Product:** HamidCognition Action Gate.

### What is being sold

The contract must explicitly define whether the transaction is:

1. a perpetual product license;
2. a source-code transfer;
3. an exclusive commercial license;
4. an IP assignment; or
5. a combined transaction.

This ClaimLab does not silently convert a product sale into an IP assignment.

## Evidence boundary

The following are engineering evidence, not commercial proof:

- successful automated tests;
- Product Gates;
- Clean-Room Verification;
- production E2E smoke;
- replay acceptance;
- evidence-pack digests;
- repository history.

The following are required to prove an actual commercial transaction:

- identified buyer;
- written offer or agreement;
- agreed scope;
- signed contract;
- payment instructions;
- blockchain transaction ID or equivalent settlement record;
- delivery/acceptance record.

## Pricing language

Do not describe 3 BTC or USD 100,000 as market value, appraised value, industry-standard price, or guaranteed valuation. They are proposed commercial terms until independently negotiated and executed.

## Acceptance trigger

A claim moves from PROPOSED to CONTRACTED only after the relevant signed agreement exists.

A sale moves from OFFERED to SOLD only after both contractual acceptance and settlement evidence are recorded.

## Change control

Any buyer-facing change to price, payment timing, IP scope, product scope, or guarantees must update this ClaimLab before publication.
