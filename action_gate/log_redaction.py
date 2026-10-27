"""Redact bearer credentials and authority envelopes from diagnostic output."""
import re


_SENSITIVE_KEY = re.compile(r"(?:token|secret|password|credential|authorization|execution_authority|api[_-]?key)", re.IGNORECASE)


def redact_for_log(value):
    """Return a JSON-compatible copy with sensitive values removed recursively."""
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if _SENSITIVE_KEY.search(str(key)) else redact_for_log(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_for_log(item) for item in value]
    return value
