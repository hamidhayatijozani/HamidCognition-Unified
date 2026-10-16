"""Deterministic integrity check for a stored artifact snapshot."""
from .claim_provenance import ClaimProvenanceEngine
from .observable_artifacts import ObservableArtifact


class ReplayVerifier:
    @staticmethod
    def verify(artifact: ObservableArtifact, expected_sha256: str) -> bool:
        if not artifact.validate():
            return False
        if not isinstance(expected_sha256, str) or len(expected_sha256) != 64:
            return False
        try:
            actual = ClaimProvenanceEngine.digest(artifact.to_dict())
        except (TypeError, ValueError):
            return False
        return actual == expected_sha256.lower()

    @staticmethod
    def fingerprint(artifact: ObservableArtifact) -> str:
        if not artifact.validate():
            raise ValueError("invalid observable artifact")
        return ClaimProvenanceEngine.digest(artifact.to_dict())
