import json
import subprocess
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "version_source_gate.py"
class VersionSourceGateTests(unittest.TestCase):
    def test_manifest_has_one_canonical_source(self):
        spec = json.loads((ROOT / "PRODUCT/VERSION_SOURCES.json").read_text())
        self.assertEqual(spec["canonical"], "action_gate/VERSION")
        self.assertNotIn(spec["canonical"], spec["derived"])
    def test_gate_passes(self):
        result = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    def test_historical_changelog_is_explicitly_ignored(self):
        spec = json.loads((ROOT / "PRODUCT/VERSION_SOURCES.json").read_text())
        self.assertIn("CHANGELOG.md", spec["ignored"])
    def test_workflow_metadata_is_explicitly_ignored(self):
        spec = json.loads((ROOT / "PRODUCT/VERSION_SOURCES.json").read_text())
        self.assertIn(".github/workflows/product-gates.yml", spec["ignored"])
    def test_version_like_pattern_catches_two_part_and_prerelease(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("version_source_gate", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertIsNotNone(module.VERSION_LIKE.search("For version 1.1"))
        self.assertIsNotNone(module.VERSION_LIKE.search("For version v1.1.2-beta.1"))
        self.assertIsNone(module.VERSION_LIKE.search("actions/checkout@v4"))
if __name__ == "__main__":
    unittest.main()
