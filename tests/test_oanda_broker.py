import os
import tempfile
import unittest
from decimal import Decimal

from action_gate.security_authority import issue_authority
from broker_runtime.models import BrokerEnvironment, BrokerExecutionState, MarketOrder
from broker_runtime.oanda import OandaBroker
from broker_runtime.risk import BrokerPolicy


class FakeResponse:
    def __init__(self, body, status=200, headers=None):
        self._body = body
        self.status_code = status
        self.headers = headers or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"http_{self.status_code}")

    def json(self):
        return self._body


class FakeTransport:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.posts = []

    def get(self, url, **kwargs):
        return self.response

    def post(self, url, **kwargs):
        self.posts.append((url, kwargs))
        if self.error:
            raise self.error
        return self.response


class OandaBrokerTests(unittest.TestCase):
    SECRET = b"test-authority-secret"
    TENANT = "tenant-a"

    def setUp(self):
        import action_gate.storage as storage

        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()
        storage.SQLITE_PATH = self._tmp.name
        storage.init_db()
        os.environ["ACTION_GATE_AUTHORITY_SECRET"] = self.SECRET.decode()

    def tearDown(self):
        try:
            os.unlink(self._tmp.name)
        except FileNotFoundError:
            pass

    def order(self, operation_id="OP-1"):
        return MarketOrder(operation_id, "EUR_USD", Decimal("100"))

    def broker(
        self,
        transport,
        environment=BrokerEnvironment.PRACTICE,
        live=False,
        confirmation="",
    ):
        return OandaBroker(
            token="test-token",
            account_id="101-001",
            environment=environment,
            live_trading_enabled=live,
            live_confirmation=confirmation,
            policy=BrokerPolicy(max_units=Decimal("1000")),
            tenant_id=self.TENANT,
            transport=transport,
        )

    def authority_for(self, broker, order=None, policy=None, nonce=None):
        order = order or self.order()
        policy = policy or broker.policy
        authority = issue_authority(
            secret=self.SECRET,
            decision_id=f"dec_{order.operation_id}",
            tenant_id=self.TENANT,
            action=broker._authorization_action(order),
            policy=policy.as_authorization_policy(),
            decision="ALLOW",
            ttl_seconds=300,
            nonce=nonce,
        )
        return authority.token()

    def response(self):
        return FakeResponse(
            {
                "lastTransactionID": "2",
                "orderCreateTransaction": {"id": "1"},
                "orderFillTransaction": {
                    "id": "2",
                    "tradeOpened": {"tradeID": "3"},
                },
            },
            status=201,
            headers={"RequestID": "REQ-1"},
        )

    def test_practice_order_requires_and_accepts_gate_authority(self):
        transport = FakeTransport(response=self.response())
        broker = self.broker(transport)
        token = self.authority_for(broker)

        result = broker.submit_market_order(self.order(), authority_token=token)

        self.assertEqual(result.state, BrokerExecutionState.FILLED)
        self.assertEqual(result.broker_order_id, "1")
        self.assertEqual(result.broker_trade_id, "3")
        self.assertEqual(result.request_id, "REQ-1")
        self.assertEqual(
            transport.posts[0][1]["json"]["order"]["clientExtensions"]["id"], "OP-1"
        )

    def test_direct_execution_without_authority_is_blocked(self):
        transport = FakeTransport()
        result = self.broker(transport).submit_market_order(self.order())
        self.assertEqual(result.state, BrokerExecutionState.BLOCKED)
        self.assertIn("action_gate_authorization_required", result.reason)
        self.assertEqual(transport.posts, [])

    def test_tampered_action_is_blocked(self):
        transport = FakeTransport(response=self.response())
        broker = self.broker(transport)
        token = self.authority_for(broker)

        result = broker.submit_market_order(
            self.order(operation_id="DIFFERENT"), authority_token=token
        )

        self.assertEqual(result.state, BrokerExecutionState.BLOCKED)
        self.assertIn("action_gate_authorization_rejected", result.reason)
        self.assertEqual(transport.posts, [])

    def test_replay_is_blocked(self):
        transport = FakeTransport(response=self.response())
        broker = self.broker(transport)
        token = self.authority_for(broker)

        first = broker.submit_market_order(self.order(), authority_token=token)
        second = broker.submit_market_order(self.order(), authority_token=token)

        self.assertEqual(first.state, BrokerExecutionState.FILLED)
        self.assertEqual(second.state, BrokerExecutionState.BLOCKED)
        self.assertIn("nonce_reuse", second.reason)
        self.assertEqual(len(transport.posts), 1)

    def test_live_mode_is_blocked_without_explicit_enablement(self):
        transport = FakeTransport()
        broker = self.broker(
            transport, environment=BrokerEnvironment.LIVE, live=False
        )
        token = self.authority_for(broker)

        result = broker.submit_market_order(self.order(), authority_token=token)

        self.assertEqual(result.state, BrokerExecutionState.BLOCKED)
        self.assertEqual(result.reason, "live_trading_disabled")
        self.assertEqual(transport.posts, [])

    def test_unknown_transport_result_is_not_retried(self):
        transport = FakeTransport(error=TimeoutError("timeout"))
        broker = self.broker(transport)
        token = self.authority_for(broker)

        result = broker.submit_market_order(self.order(), authority_token=token)

        self.assertEqual(result.state, BrokerExecutionState.UNKNOWN)
        self.assertEqual(len(transport.posts), 1)

    def test_risk_limit_blocks_before_authority_or_network(self):
        transport = FakeTransport()
        broker = self.broker(transport)
        oversized = self.order(operation_id="OP-2")
        oversized = MarketOrder("OP-2", "EUR_USD", Decimal("1001"))
        token = self.authority_for(broker, order=oversized)

        with self.assertRaisesRegex(ValueError, "max_units_exceeded"):
            broker.submit_market_order(oversized, authority_token=token)

        self.assertEqual(transport.posts, [])


if __name__ == "__main__":
    unittest.main()
