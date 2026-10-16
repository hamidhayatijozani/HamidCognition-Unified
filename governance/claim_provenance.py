"""Small deterministic provenance helper; hashes are not digital signatures."""
import hashlib
import json
from typing import Any


class ClaimProvenanceEngine:
    @staticmethod
    def digest(payload: dict[str, Any]) -> str:
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False, allow_nan=False).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def attach(self, claim: dict[str, Any], evidence: list[dict[str, Any]]) -> dict[str, Any]:
        evidence_ids = {item.get("id") for item in evidence if item.get("id") is not None}
        refs = claim.get("evidence_refs", [])
        if not isinstance(refs, list) or any(ref not in evidence_ids for ref in refs):
            raise ValueError("claim references missing evidence")
        result = dict(claim)
        result["provenance_sha256"] = self.digest({"claim": claim, "evidence": evidence})
        return result
