from __future__ import annotations
from decimal import Decimal
from difflib import SequenceMatcher
from typing import Iterable
from .models import FinancialEvent, MatchCandidate

def _text_score(a: str | None, b: str | None) -> Decimal:
    if not a or not b:
        return Decimal("0")
    ratio = SequenceMatcher(None, a.strip().casefold(), b.strip().casefold()).ratio()
    return Decimal(str(ratio)).quantize(Decimal("0.001"))

def deterministic_candidates(source: FinancialEvent, targets: Iterable[FinancialEvent]) -> tuple[MatchCandidate, ...]:
    out = []
    for target in targets:
        if source.amount != target.amount or source.currency != target.currency:
            continue
        reasons = ["amount_exact", "currency_exact"]
        if source.reference and target.reference and source.reference == target.reference:
            reasons.append("reference_exact")
        if source.account_ref and target.account_ref and source.account_ref == target.account_ref:
            reasons.append("account_exact")
        out.append(MatchCandidate(source.event_id, target.event_id, Decimal("1.000"), tuple(reasons)))
    return tuple(out)

def ambiguous_candidates(source: FinancialEvent, targets: Iterable[FinancialEvent]) -> tuple[MatchCandidate, ...]:
    out = []
    for target in targets:
        if source.amount != target.amount or source.currency != target.currency:
            continue
        score = _text_score(source.counterparty or source.description, target.counterparty or target.description)
        if score <= Decimal("0"):
            continue
        out.append(MatchCandidate(source.event_id, target.event_id, score, ("amount_exact", "currency_exact", "text_similarity")))
    return tuple(sorted(out, key=lambda x: x.score, reverse=True))
