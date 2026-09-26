# USDT Payment Policy

## Scope

HamidCognition commercial payments are settled in USDT only.

The payment system is intentionally separated from the runtime security boundary. Action Gate never needs custody of funds and never receives wallet private keys.

## Required configuration

The commercial operator configures the receiving wallet outside source control:

- `USDT_PAYMENT_ADDRESS`
- `USDT_NETWORK`
- `USDT_CONFIRMATIONS_REQUIRED`

The actual wallet address and private keys must never be committed to Git.

## Invoice lifecycle

`ISSUED -> AWAITING_PAYMENT -> PAYMENT_DETECTED -> CONFIRMED -> ENTITLED`

Any conflicting, underpaid, wrong-network or otherwise unverifiable transaction remains `EXCEPTION` until manually reconciled.

## Minimum payment evidence

Each paid invoice records:

- invoice ID;
- quoted amount in USDT;
- network;
- receiving address fingerprint;
- transaction hash;
- block/transaction reference;
- confirmation count;
- timestamp;
- product version;
- entitlement identifier.

The transaction hash is the settlement reference. A screenshot, copied address, or chat message is not settlement proof.

## Safety rules

- Never request or store a wallet seed phrase or private key.
- Never silently substitute a different USDT network.
- Display the network and receiving address together before payment.
- Treat a payment sent on the wrong network as an exception, not as automatically settled.
- Do not release commercial credentials or artifacts until the invoice reaches `CONFIRMED`.
- Keep payment verification outside the Action Gate authorization path.

## Current deployment contract

The repository provides the payment contract and operational boundary. A live receiving address is deployment configuration and must be supplied through the commercial operator's secret/configuration system, not Git.
