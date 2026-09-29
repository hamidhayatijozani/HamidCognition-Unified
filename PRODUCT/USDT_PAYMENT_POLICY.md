# Payment & Settlement Policy

## Scope

HamidCognition separates commercial settlement from the runtime security boundary. Action Gate never needs custody of funds and never receives wallet private keys.

## Current operator settlement account

The operator currently has one verified TopChange settlement identifier:

- Provider: TopChange
- Wallet name: کیف پول دلار
- Wallet ID: `USD2134914`
- Identifier type: TopChange wallet/account identifier

This identifier is **not a blockchain address**. The product must not present it as a USDT on-chain receiving address.

## Current payment mode

Until a real blockchain receiving address and network are configured, payment verification is **manual/provider-based**.

The system may issue an invoice and record:

- invoice ID;
- quoted amount and currency;
- provider: TopChange;
- settlement account identifier;
- payment/reference information supplied by the provider;
- timestamp;
- product version;
- entitlement identifier;
- verification status;
- operator verification evidence.

The system must not mark a payment CONFIRMED merely from a customer screenshot, copied identifier, or chat message.

## Optional on-chain USDT mode

If a real USDT receiving address is configured later, the following fields become required:

- `USDT_PAYMENT_ADDRESS`
- `USDT_NETWORK`
- `USDT_CONFIRMATIONS_REQUIRED`

For on-chain settlement, the transaction hash is the settlement reference and confirmation evidence must be recorded.

## Invoice lifecycle

`ISSUED -> AWAITING_PAYMENT -> PAYMENT_DETECTED -> CONFIRMED -> ENTITLED`

Any conflicting, underpaid, wrong-network, provider-unverified, or otherwise unverifiable transaction remains `EXCEPTION` until manually reconciled.

## Safety rules

- Never request or store a wallet seed phrase or private key.
- Never invent or infer a blockchain address from a TopChange Wallet ID.
- Never silently substitute a different network.
- Do not release commercial credentials or artifacts until settlement reaches `CONFIRMED`.
- Keep payment verification outside the Action Gate authorization path.

## Current truth

The repository contains the payment contract and the operator's TopChange Wallet ID metadata. It does **not** claim that the operator currently has a blockchain USDT receiving address.

A live on-chain address, if later supplied, remains deployment configuration and must not be committed to Git.
