from __future__ import annotations
from decimal import Decimal, InvalidOperation
from typing import Any
from .models import FinancialEvent

def _decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value)).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"invalid monetary amount: {value!r}") from exc

def bank_row_to_event(row: dict[str, Any]) -> FinancialEvent:
    event_id = str(row.get("transaction_id") or row.get("reference") or "").strip()
    if not event_id:
        raise ValueError("bank row requires transaction_id or reference")
    return FinancialEvent(
        event_id=event_id,
        source="bank",
        occurred_at=str(row["date"]),
        amount=_decimal(row["amount"]),
        currency=str(row.get("currency", "IRR")).upper(),
        reference=str(row.get("reference")) if row.get("reference") is not None else None,
        account_ref=str(row.get("account_ref")) if row.get("account_ref") is not None else None,
        counterparty=str(row.get("counterparty")) if row.get("counterparty") is not None else None,
        description=str(row.get("description")) if row.get("description") is not None else None,
        raw=dict(row),
    )
