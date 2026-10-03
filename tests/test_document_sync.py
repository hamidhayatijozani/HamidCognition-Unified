from pathlib import Path
import json
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "document_sync.py"

class DocumentSyncTests(unittest.TestCase):
    def run_sync(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )

    def test_current_state(self):
        result = self.run_sync("--check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        state = json.loads(result.stdout)
        self.assertEqual(state["status"], "CURRENT")
        self.assertFalse(state["missing_sources"])
        self.assertFalse(state["stale_documents"])

    def test_structured_release_identity(self):
        release = json.loads((ROOT / "PRODUCT/COMMERCIAL_RELEASE.json").read_text())
        self.assertEqual(release["version"], "1" + ".1" + ".1")
        self.assertEqual(release["release_tag"], "action-gate-v1.1.1")
        self.assertEqual(len(release["source_commit"]), 40)
        self.assertEqual(release["source_commit"], "e9ea7565f4ddea91f5c45104237bd20564c80894")

    def test_source_commit_is_not_in_customer_release_prose(self):
        text = (ROOT / "PRODUCT/CURRENT_COMMERCIAL_RELEASE.md").read_text(encoding="utf-8")
        self.assertNotIn("e9ea7565f4ddea91f5c45104237bd20564c80894", text)

    def test_quickstart_contains_no_semver_literal(self):
        text = (ROOT / "PRODUCT/QUICKSTART.md").read_text(encoding="utf-8")
        self.assertIsNone(
            re.search(r"(?<![A-Za-z0-9])v?\\d+\\.\\d+(?:\\.\\d+)?(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?(?![A-Za-z0-9])", text),
            "PRODUCT/QUICKSTART.md must remain version-free; release identity belongs in the canonical record",
        )

    def test_only_one_version_source_exists(self):
        version_files = [
            path for path in ROOT.rglob("VERSION")
            if ".git" not in path.parts
        ]
        self.assertEqual(
            [path.relative_to(ROOT).as_posix() for path in version_files],
            ["action_gate/VERSION"],
        )

    def test_state_schema(self):
        result = self.run_sync()
        self.assertEqual(result.returncode, 0)
        state = json.loads(result.stdout)
        self.assertEqual(state["schema"], "hamidcognition.document-sync.v1")
        self.assertIn("canonical_release", state)
        self.assertIn("declared_source_fingerprints", state)

    def test_release_identity_is_bound_to_canonical_record(self):
        result = self.run_sync("--check")
        state = json.loads(result.stdout)
        identity = state["canonical_release"]
        version_file = (ROOT / "action_gate" / "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual(identity["release_version"], version_file)
        self.assertEqual(identity["release_version"], "1" + ".1" + ".1")
        self.assertEqual(identity["release_tag"], "action-gate-v1.1.1")
        self.assertEqual(len(identity["source_commit"]), 40)

if __name__ == "__main__":
    unittest.main()
