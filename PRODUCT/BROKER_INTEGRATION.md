# Broker Integration Boundary

HamidCognition includes an OANDA v20 broker execution adapter.

Execution boundary:

Agent/Strategy -> Action Gate -> OANDA Broker Adapter -> OANDA v20 -> Market

The adapter is deliberately fail-closed.

## Current implementation

- OANDA Practice and Live API environments.
- Account and pricing endpoints.
- Market orders with optional stop-loss and take-profit.
- Gate-issued execution authority is mandatory before dispatch.
- The broker verifies authority signature, tenant binding, action binding, policy binding, expiry, decision and single-use nonce before dispatch.
- A boolean `gate_authorized` flag is not accepted by the broker execution API.
- Deterministic instrument and unit limits.
- Operation ID is carried into OANDA client extensions.
- A transport failure after dispatch is reported as UNKNOWN and is never automatically retried.
- Live execution requires both LIVE_TRADING_ENABLED=true and LIVE_TRADING_CONFIRMATION=LIVE.
- Practice mode is the default.
- No credentials are stored in GitHub.

OANDA documents separate Practice and production REST base URLs and recommends the Practice environment for testing.

## Environment

Use deployment-only secrets:

- OANDA_API_TOKEN
- OANDA_ACCOUNT_ID
- OANDA_ENVIRONMENT=practice
- LIVE_TRADING_ENABLED=false
- LIVE_TRADING_CONFIRMATION=

Never commit the token or account credentials.

## Acceptance sequence

1. Run unit tests with mocked broker transport.
2. Configure an OANDA Practice account and token.
3. Call account and pricing endpoints.
4. Submit one controlled Practice market order through Action Gate.
5. Verify the broker response and resulting trade.
6. Record request ID, broker order ID, trade ID, operation ID and evidence.
7. Only after Practice acceptance may a customer independently enable Live mode.

OANDA's v20 REST API provides account information, pricing and order creation.

This repository does not claim that a live broker account has been connected or that a real-money order has been executed until corresponding external evidence exists.
