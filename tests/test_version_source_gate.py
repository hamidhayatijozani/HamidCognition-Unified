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
if __name__ == "__main__":
    unittest.main()
