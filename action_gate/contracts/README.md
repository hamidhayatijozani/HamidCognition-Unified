# HHJ-CSG Contract v1.0

The POC uses a versioned contract-first vertical slice.

- `permission_request.schema.json` defines the ingress shape and bounds.
- `decision.schema.json` defines the Decision Object and explicitly separates digest fields from the HMAC signature.
- `../canonicalization.py` implements `JCS-LIKE-1`: UTF-8 JSON, sorted keys, compact separators, `ensure_ascii=false`, `allow_nan=false`.
- Permission-request timestamps are contractually represented as UTC RFC3339 strings ending in `Z`.

Digest and signature semantics:

`request_digest = SHA-256(canonical(permission_request))`

`decision_digest = SHA-256(canonical(decision_without(decision_digest, signature)))`

`signature = HMAC-SHA256(canonical({request_digest, decision_digest, decision_id, tenant_id, nonce}))`

The signature is not a digest. `key_id`, `signature_algorithm`, and `canonicalization_version` are carried in the Decision Object so verification is versioned and auditable.

The POC does not claim RFC 8785 JSON Canonicalization Scheme compatibility. `JCS-LIKE-1` is deliberately a distinct contract version.
