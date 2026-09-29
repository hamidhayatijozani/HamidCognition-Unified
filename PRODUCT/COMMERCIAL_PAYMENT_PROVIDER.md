# Commercial Payment Provider

## Settlement account

HamidCognition has one operator-supplied TopChange settlement account for commercial payment handling.

- Provider: TopChange
- Wallet name: کیف پول دلار
- Wallet ID: `USD2134914`
- Identifier type: TopChange wallet/account identifier
- Source: Wallet Ownership Certificate supplied by the operator

## Boundary

`USD2134914` is an account/wallet identifier at TopChange. It is **not** a blockchain address and must not be placed in:

- `USDT_PAYMENT_ADDRESS`
- `USDT_NETWORK`

The repository therefore does not treat this identifier as proof of an on-chain USDT receiving address.

If a blockchain USDT receiving address is later required, it must be supplied separately together with its exact network and configured outside source control.

## Security

No seed phrase, private key, password, API secret, or other credential is stored in this repository.

The TopChange Wallet ID is operational metadata only. Payment settlement evidence must still use the transaction hash and network-specific verification defined in `PRODUCT/USDT_PAYMENT_POLICY.md`.

## Ownership evidence

The operator supplied a TopChange Wallet Ownership Certificate stating that the listed wallet was verified and approved as belonging to the named holder. The certificate itself is not committed to this repository, and personal contact information from the certificate is intentionally excluded from public product metadata.
