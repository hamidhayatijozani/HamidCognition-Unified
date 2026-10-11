# Commercial Payment Provider

## Settlement account

HamidCognition uses an operator-supplied TopChange settlement account for commercial payment handling.

- Provider: TopChange
- Identifier type: provider wallet/account identifier, configured out of band
- Source: operator-provided ownership evidence, retained outside public source control

## Boundary

The TopChange account identifier is operational metadata. It is **not** a blockchain address and must not be placed in:

- `USDT_PAYMENT_ADDRESS`
- `USDT_NETWORK`

The repository therefore does not treat this identifier as proof of an on-chain USDT receiving address.

If a blockchain USDT receiving address is later required, it must be supplied separately together with its exact network and configured outside source control.

## Security

No seed phrase, private key, password, API secret, or other credential is stored in this repository.

The provider account identifier is configured outside source control. Payment settlement evidence must still use the appropriate provider reference or, for on-chain payment, the transaction hash and network-specific verification defined in `PRODUCT/USDT_PAYMENT_POLICY.md`.

## Ownership evidence

The operator supplied a TopChange Wallet Ownership Certificate stating that the listed wallet was verified and approved as belonging to the named holder. The certificate itself is not committed to this repository, and personal contact information from the certificate is intentionally excluded from public product metadata.
