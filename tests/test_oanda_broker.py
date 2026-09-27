import unittest
from decimal import Decimal

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
    def order(self):
        return MarketOrder("OP-1", "EUR_USD", Decimal("100"))

    def broker(self, transport, environment=BrokerEnvironment.PRACTICE, live=False, confirmation=""):
        return OandaBroker(
            token="test-token",
            account_id="101-001",
            environment=environment,
            live_trading_enabled=live,
            live_confirmation=confirmation,
            policy=BrokerPolicy(max_units=Decimal("1000")),
            transport=transport,
        )

    def test_practice_order_can_be_submitted_when_gate_authorizes(self):
        response = FakeResponse(
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
        transport = FakeTransport(response=response)
        result = self.broker(transport).submit_market_order(
            self.order(), gate_authorized=True
        )
        self.assertEqual(result.state, BrokerExecutionState.FILLED)
        self.assertEqual(result.broker_order_id, "1")
        self.assertEqual(result.broker_trade_id, "3")
        self.assertEqual(result.request_id, "REQ-1")
        self.assertEqual(
            transport.posts[0][1]["json"]["order"]["clientExtensions"]["id"], "OP-1"
        )

    def test_direct_execution_without_gate_is_blocked(self):
        transport = FakeTransport()
        result = self.broker(transport).submit_market_order(
            self.order(), gate_authorized=False
        )
        self.assertEqual(result.state, BrokerExecutionState.BLOCKED)
        self.assertEqual(transport.posts, [])

    def test_live_mode_is_blocked_without_explicit_enablement(self):
        transport = FakeTransport()
        result = self.broker(
            transport, environment=BrokerEnvironment.LIVE, live=False
        ).submit_market_order(self.order(), gate_authorized=True)
        self.assertEqual(result.state, BrokerExecutionState.BLOCKED)
        self.assertEqual(result.reason, "live_trading_disabled")
        self.assertEqual(transport.posts, [])

    def test_unknown_transport_result_is_not_retried(self):
        transport = FakeTransport(error=TimeoutError("timeout"))
        result = self.broker(transport).submit_market_order(
            self.order(), gate_authorized=True
        )
        self.assertEqual(result.state, BrokerExecutionState.UNKNOWN)
        self.assertEqual(len(transport.posts), 1)

    def test_risk_limit_blocks_before_network(self):
        transport = FakeTransport()
        broker = self.broker(transport)
        with self.assertRaisesRegex(ValueError, "max_units_exceeded"):
            broker.submit_market_order(
                MarketOrder("OP-2", "EUR_USD", Decimal("1001")),
                gate_authorized=True,
            )
        self.assertEqual(transport.posts, [])


if __name__ == "__main__":
    unittest.main()
