import json
import subprocess
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "version_source_gate.py"
class VersionSourceGateTests(unittest.TestCase):
    def load_module(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("version_source_gate", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_manifest_has_one_canonical_source(self):
        spec = json.loads((ROOT / "PRODUCT/VERSION_SOURCES.json").read_text())
        self.assertEqual(spec["canonical"], "action_gate/VERSION")
        self.assertNotIn(spec["canonical"], spec["derived"])
        self.assertIn(".github/workflows/**", spec["env_metadata"])
    def test_gate_passes(self):
        result = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    def test_historical_changelog_is_explicitly_ignored(self):
        spec = json.loads((ROOT / "PRODUCT/VERSION_SOURCES.json").read_text())
        self.assertIn("CHANGELOG.md", spec["ignored"])
    def test_workflow_metadata_is_explicitly_ignored(self):
        spec = json.loads((ROOT / "PRODUCT/VERSION_SOURCES.json").read_text())
        self.assertIn(".github/workflows/**", spec["env_metadata"])
    def test_product_context_is_required(self):
        module = self.load_module()
        two_part = "For product version " + "1" + ".1"
        prerelease = "For version v" + "1" + ".1" + ".2-beta." + "1"
        self.assertIsNotNone(module.VERSION_LIKE.search(two_part))
        self.assertIsNotNone(module.VERSION_LIKE.search(prerelease))
        match = module.VERSION_LIKE.search(two_part)
        self.assertTrue(module.has_product_context(two_part, match.start(), match.end()))
        for text, start, end in [
            ("Python 3.11 is required", 7, 11),
            ("pytest 8.0 is installed", 7, 10),
            ("Ubuntu 22.04 runner", 7, 12),
            ("HTTP/1.1 protocol", 5, 8),
            ("CVE-2024.1234", 4, 13),
            ("actions/checkout@v4", 18, 20),
        ]:
            self.assertFalse(module.has_product_context(text, start, end), text)

if __name__ == "__main__":
    unittest.main()
