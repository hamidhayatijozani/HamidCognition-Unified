# Semi-Automatic Sale and Automatic Delivery

## Purpose

HamidCognition defines a provider-neutral sale state machine that works with the
current TopChange settlement boundary without pretending that TopChange exposes
a verified webhook/API integration.

Current settlement account:
- Provider: TopChange
- Wallet name: کیف پول دلار
- Wallet ID: USD2134914
- This identifier is not a blockchain address.

## Customer flow

1. Create immutable invoice for product/version, amount and currency.
2. Customer pays using the supplied provider instructions.
3. Payment evidence enters PAYMENT_REVIEW.
4. Trusted operator/provider verification changes the sale to CONFIRMED.
5. The system automatically issues a one-time entitlement.
6. The system automatically prepares delivery using the exact product version and artifact digest.
7. Delivery is recorded as evidence.
8. Customer acceptance can close the sale.

The only human step in the current mode is trusted payment verification.

## Hard safety rules

- Customer screenshots, chat messages, or copied wallet identifiers never constitute payment confirmation.
- USD2134914 must never be treated as a blockchain address.
- No entitlement or artifact delivery occurs before CONFIRMED.
- Amount and currency must match the invoice exactly.
- Entitlement issuance is idempotent for an existing sale.
- Delivery records the exact artifact digest.
- No seed, private key, password, or payment credential is stored.
- Provider automation can later use WEBHOOK or API_POLL without changing the sale state machine.

## Commercial truth boundary

This is semi-automatic payment with automatic delivery, not fully automatic payment processing.
