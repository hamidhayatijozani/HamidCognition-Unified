# USDT Invoice Template

## Invoice

- Invoice ID: `<invoice-id>`
- Product: HamidCognition Action Gate
- Version: `<version>`
- Delivery mode: `SELF_HOSTED | MANAGED | ENTERPRISE`
- Amount due: `<amount> USDT`
- Network: `<USDT network>`
- Receiving address: `<configured receiving address>`
- Payment deadline: `<UTC timestamp>`

## Settlement

Customer supplies:

- transaction hash;
- sending address;
- timestamp.

Operator verifies:

1. the transaction exists on the stated network;
2. the recipient matches the configured receiving address;
3. the received amount is sufficient;
4. the confirmation requirement is satisfied;
5. the transaction has not already been assigned to another invoice.

Only then is the invoice marked `CONFIRMED` and the delivery entitlement activated.
