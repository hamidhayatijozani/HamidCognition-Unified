from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts.verify_release_manifest import read_readiness_sha, verify


SOURCE_SHA = "a" * 40
OTHER_SHA = "b" * 40
VERSION = "1.2.3"


class ReleaseManifestVerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.archive = self.root / f"action-gate-{VERSION}.tar"
        self.archive.write_bytes(b"release artifact bytes")
        digest = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.checksum = self.root / f"{self.archive.name}.sha256"
        self.checksum.write_text(f"{digest}  {self.archive.name}\n", encoding="utf-8")
        self.manifest = self.root / f"action-gate-{VERSION}.manifest.txt"
        self.write_manifest()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_manifest(self, **overrides: str) -> None:
        values = {
            "product": "HamidCognition Action Gate",
            "version": VERSION,
            "commit": SOURCE_SHA,
            "release_readiness_run_id": "123456",
            "image": f"action-gate:{VERSION}",
            "archive": self.archive.name,
            "generated_at": "2026-10-12T00:00:00Z",
        }
        values.update(overrides)
        self.manifest.write_text(
            "".join(f"{key}={value}\n" for key, value in values.items()),
            encoding="utf-8",
        )

    def verify_candidate(self, expected_sha: str = SOURCE_SHA,
                         expected_version: str = VERSION,
                         readiness_sha: str = SOURCE_SHA) -> None:
        verify(self.manifest, self.archive, self.checksum,
               expected_sha, expected_version, readiness_sha)

    def test_accepts_consistent_candidate(self) -> None:
        self.verify_candidate()

    def test_rejects_missing_readiness_evidence_file(self) -> None:
        with self.assertRaisesRegex(ValueError, "readiness evidence file is missing"):
            read_readiness_sha(self.root / "missing-validated-sha.txt")

    def test_rejects_malformed_readiness_evidence_file(self) -> None:
        evidence = self.root / "validated-sha.txt"
        evidence.write_text("not-a-git-sha\\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "full lowercase Git SHA"):
            read_readiness_sha(evidence)


    def test_rejects_manifest_sha_mismatch(self) -> None:
        self.write_manifest(commit=OTHER_SHA)
        with self.assertRaisesRegex(ValueError, "source SHA"):
            self.verify_candidate()

    def test_rejects_readiness_sha_mismatch(self) -> None:
        with self.assertRaisesRegex(ValueError, "source SHA"):
            self.verify_candidate(readiness_sha=OTHER_SHA)

    def test_rejects_expected_sha_mismatch(self) -> None:
        with self.assertRaisesRegex(ValueError, "source SHA"):
            self.verify_candidate(expected_sha=OTHER_SHA)

    def test_rejects_version_mismatch(self) -> None:
        with self.assertRaisesRegex(ValueError, "version"):
            self.verify_candidate(expected_version="9.9.9")

    def test_rejects_manifest_archive_name_mismatch(self) -> None:
        self.write_manifest(archive="different.tar")
        with self.assertRaisesRegex(ValueError, "archive name"):
            self.verify_candidate()

    def test_rejects_missing_manifest_field(self) -> None:
        self.manifest.write_text("version=1.2.3\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "missing manifest fields"):
            self.verify_candidate()

    def test_rejects_duplicate_manifest_key(self) -> None:
        with self.manifest.open("a", encoding="utf-8") as stream:
            stream.write(f"commit={SOURCE_SHA}\n")
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.verify_candidate()

    def test_rejects_tampered_archive(self) -> None:
        self.archive.write_bytes(b"tampered artifact")
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            self.verify_candidate()

    def test_rejects_checksum_for_another_filename(self) -> None:
        digest = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.checksum.write_text(f"{digest}  another.tar\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "checksum filename"):
            self.verify_candidate()

    def test_rejects_malformed_checksum(self) -> None:
        self.checksum.write_text("not-a-checksum\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "checksum record"):
            self.verify_candidate()


if __name__ == "__main__":
    unittest.main()
