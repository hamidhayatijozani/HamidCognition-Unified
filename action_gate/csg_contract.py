from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from canonicalization import CANONICALIZATION_VERSION, KEY_ID, SIGNATURE_ALGORITHM, sha256_digest

CONTRACT_VERSION = "hhj-csg/1.0"
ALGORITHM_VERSION = "hhj-csg-decision/1.0"


class PermissionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_version: Literal[CONTRACT_VERSION]
    request_id: str = Field(pattern=r"^[A-Za-z0-9._:-]{1,128}$")
    tenant_id: str = Field(min_length=1, max_length=128)
    agent_id: str = Field(min_length=1, max_length=128)
    actor_id: str | None = Field(default=None, max_length=128)
    action: str = Field(min_length=1, max_length=256)
    target: str | None = Field(default=None, max_length=2048)
    timestamp: datetime
    parameters: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)
    evidence: list[dict[str, Any]] = Field(default_factory=list, max_length=100)
    risk_hint: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] | None = None

    @field_validator("parameters", "context")
    @classmethod
    def bounded_objects(cls, value: dict[str, Any]) -> dict[str, Any]:
        if len(value) > 100:
            raise ValueError("object_property_limit_exceeded")
        return value


class DecisionObject(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_version: Literal[CONTRACT_VERSION]
    decision_id: str = Field(pattern=r"^dec_[A-Za-z0-9]{8,128}$")
    request_id: str = Field(max_length=128)
    tenant_id: str = Field(min_length=1, max_length=128)
    decision: Literal["ALLOW", "DENY", "ASK", "SANDBOX"]
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    request_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    decision_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    signature: str = Field(pattern=r"^[a-f0-9]{64}$")
    signature_algorithm: Literal[SIGNATURE_ALGORITHM]
    key_id: str = Field(min_length=1, max_length=128)
    canonicalization_version: Literal[CANONICALIZATION_VERSION]
    policy_version: str = Field(min_length=1, max_length=128)
    algorithm_version: Literal[ALGORITHM_VERSION]
    issued_at: datetime
    expires_at: datetime
    nonce: str = Field(pattern=r"^[a-f0-9]{32}$")
    metrics_snapshot: dict[str, Any] = Field(default_factory=dict)
    execution_receipt: dict[str, Any] | None = None
    constraints: list[str] = Field(default_factory=list, max_length=100)

    @staticmethod
    def digest_without_digest_fields(payload: dict[str, Any]) -> str:
        unsigned = dict(payload)
        unsigned.pop("decision_digest", None)
        unsigned.pop("signature", None)
        return sha256_digest(unsigned)
