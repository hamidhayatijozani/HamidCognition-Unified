import unittest

from log_redaction import redact_for_log


class RedactForLogTests(unittest.TestCase):
    def test_redacts_execution_authority_and_nested_credentials(self):
        source = {
            "decision": "ALLOW",
            "execution_authority": "signed-bearer-token",
            "nested": {"Authorization": "Bearer secret", "safe": "evidence"},
            "events": [{"api_key": "private", "count": 3}],
        }
        safe = redact_for_log(source)
        self.assertEqual(safe["decision"], "ALLOW")
        self.assertEqual(safe["execution_authority"], "[REDACTED]")
        self.assertEqual(safe["nested"]["Authorization"], "[REDACTED]")
        self.assertEqual(safe["nested"]["safe"], "evidence")
        self.assertEqual(safe["events"][0]["api_key"], "[REDACTED]")
        self.assertEqual(source["execution_authority"], "signed-bearer-token")


if __name__ == "__main__":
    unittest.main()
