from src.commercial_sale import PaymentEvidence, VerificationMode, SaleStatus, create_invoice

def test_manual_payment_then_automatic_delivery():
    sale = create_invoice("buyer@example.test", "Action Gate", "v1.0.10", "100")
    assert sale.status == SaleStatus.AWAITING_PAYMENT
    sale.submit_payment(PaymentEvidence("provider-ref-001", "100", "USDT", True, VerificationMode.MANUAL_PROVIDER, "operator"))
    sale.verify_payment("operator")
    sale.issue_entitlement("SELF_HOSTED")
    sale.deliver("sha256:artifact")
    assert sale.status == SaleStatus.DELIVERED
    assert sale.delivery_digest == "sha256:artifact"

def test_unverified_payment_never_entitles():
    sale = create_invoice("buyer@example.test", "Action Gate", "v1.0.10", "100")
    sale.submit_payment(PaymentEvidence("customer-claimed-ref", "100", "USDT", False, VerificationMode.MANUAL_PROVIDER, ""))
    try:
        sale.verify_payment("operator")
    except ValueError as exc:
        assert str(exc) == "payment_not_verified"
    assert sale.status == SaleStatus.EXCEPTION
    assert sale.entitlement is None

def test_wrong_amount_blocks_delivery():
    sale = create_invoice("buyer@example.test", "Action Gate", "v1.0.10", "100")
    sale.submit_payment(PaymentEvidence("provider-ref-002", "99", "USDT", True, VerificationMode.MANUAL_PROVIDER, "operator"))
    try:
        sale.verify_payment("operator")
    except ValueError as exc:
        assert str(exc) == "amount_mismatch"
    assert sale.status == SaleStatus.EXCEPTION
