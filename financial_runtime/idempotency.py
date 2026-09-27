from __future__ import annotations
import hashlib
import json
from typing import Any

class IdempotencyVault:
    def __init__(self) -> None:
        self._operations: dict[str, dict[str, Any]] = {}

    @staticmethod
    def operation_hash(payload: dict[str, Any]) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def reserve(self, payload: dict[str, Any]) -> tuple[str, bool]:
        op_hash = self.operation_hash(payload)
        if op_hash in self._operations:
            return op_hash, False
        self._operations[op_hash] = {"state": "RESERVED", "payload": payload}
        return op_hash, True

    def state(self, operation_hash: str) -> str | None:
        record = self._operations.get(operation_hash)
        return record["state"] if record else None

    def update(self, operation_hash: str, state: str) -> None:
        if operation_hash not in self._operations:
            raise KeyError("operation not reserved")
        self._operations[operation_hash]["state"] = state
