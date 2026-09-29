"""Semi-automatic commercial sale state machine."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from enum import Enum
from hashlib import sha256
import json
import secrets
from typing import Any

class SaleStatus(str, Enum):
    DRAFT = "DRAFT"
    AWAITING_PAYMENT = "AWAITING_PAYMENT"
    PAYMENT_REVIEW = "PAYMENT_REVIEW"
    CONFIRMED = "CONFIRMED"
    ENTITLED = "ENTITLED"
    DELIVERED = "DELIVERED"
    ACCEPTED = "ACCEPTED"
    EXCEPTION = "EXCEPTION"

class VerificationMode(str, Enum):
    MANUAL_PROVIDER = "MANUAL_PROVIDER"
    WEBHOOK = "WEBHOOK"
    API_POLL = "API_POLL"

@dataclass(frozen=True)
class Invoice:
    invoice_id: str
    buyer: str
    product: str
    version: str
    amount: str
    currency: str
    provider: str
    settlement_account: str

@dataclass(frozen=True)
class PaymentEvidence:
    reference: str
    amount: str
    currency: str
    verified: bool
    mode: VerificationMode
    verified_by: str

@dataclass(frozen=True)
class Entitlement:
    entitlement_id: str
    invoice_id: str
    product: str
    version: str
    scope: str

@dataclass
class Sale:
    invoice: Invoice
    status: SaleStatus = SaleStatus.DRAFT
    payment: PaymentEvidence | None = None
    entitlement: Entitlement | None = None
    delivery_token: str | None = None
    delivery_digest: str | None = None

    def issue(self) -> "Sale":
        if self.status != SaleStatus.DRAFT:
            raise ValueError("invalid_transition")
        self.status = SaleStatus.AWAITING_PAYMENT
        return self

    def submit_payment(self, evidence: PaymentEvidence) -> "Sale":
        if self.status != SaleStatus.AWAITING_PAYMENT:
            raise ValueError("payment_not_expected")
        self.payment = evidence
        self.status = SaleStatus.PAYMENT_REVIEW
        return self

    def verify_payment(self, operator: str) -> "Sale":
        if self.status != SaleStatus.PAYMENT_REVIEW or self.payment is None:
            raise ValueError("payment_not_reviewable")
        if not self.payment.verified:
            self.status = SaleStatus.EXCEPTION
            raise ValueError("payment_not_verified")
        if self.payment.amount != self.invoice.amount:
            self.status = SaleStatus.EXCEPTION
            raise ValueError("amount_mismatch")
        if self.payment.currency.upper() != self.invoice.currency.upper():
            self.status = SaleStatus.EXCEPTION
            raise ValueError("currency_mismatch")
        if not operator.strip():
            raise ValueError("verifier_required")
        self.status = SaleStatus.CONFIRMED
        return self

    def issue_entitlement(self, scope: str) -> "Sale":
        if self.status != SaleStatus.CONFIRMED:
            raise ValueError("payment_not_confirmed")
        if self.entitlement is not None:
            return self
        self.entitlement = Entitlement(
            entitlement_id="ent_" + secrets.token_hex(12),
            invoice_id=self.invoice.invoice_id,
            product=self.invoice.product,
            version=self.invoice.version,
            scope=scope,
        )
        self.status = SaleStatus.ENTITLED
        return self

    def deliver(self, artifact_digest: str) -> "Sale":
        if self.status != SaleStatus.ENTITLED or self.entitlement is None:
            raise ValueError("not_entitled")
        if not artifact_digest.strip():
            raise ValueError("artifact_digest_required")
        self.delivery_token = secrets.token_urlsafe(24)
        self.delivery_digest = artifact_digest
        self.status = SaleStatus.DELIVERED
        return self

    def accept(self) -> "Sale":
        if self.status != SaleStatus.DELIVERED:
            raise ValueError("not_delivered")
        self.status = SaleStatus.ACCEPTED
        return self

    def audit(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["status"] = self.status.value
        payload["event_hash"] = sha256(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode()
        ).hexdigest()
        return payload

def create_invoice(
    buyer: str, product: str, version: str, amount: str,
    currency: str = "USDT", provider: str = "TopChange",
    settlement_account: str = "USD2134914",
) -> Sale:
    if not all(x.strip() for x in (buyer, product, version, amount, currency, provider, settlement_account)):
        raise ValueError("invoice_fields_required")
    return Sale(Invoice(
        invoice_id="inv_" + secrets.token_hex(10),
        buyer=buyer.strip(), product=product.strip(), version=version.strip(),
        amount=amount.strip(), currency=currency.strip().upper(),
        provider=provider.strip(), settlement_account=settlement_account.strip(),
    )).issue()
